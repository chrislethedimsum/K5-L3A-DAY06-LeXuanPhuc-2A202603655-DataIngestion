"""Pipeline orchestration for Day 06: Data Ingestion."""
import json
import os
import time
from pathlib import Path
from dotenv import load_dotenv

from .ingestion import load_pdf
from .chunking import fixed_size, by_paragraph
from .embeddings import MyEmbedder
from .store import PgVectorStore
from .evaluation import evaluate_query, summarize

load_dotenv()


def main() -> None:
    # 1. Định vị file dữ liệu và benchmark
    base_dir = Path(__file__).resolve().parent.parent
    pdf_path = base_dir / "data" / "34-2018-qh14..pdf"
    benchmark_path = base_dir / "benchmark" / "questions.json"
    results_dir = base_dir / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    # 2. Khởi tạo Database và Embedder
    db_url = os.getenv("DATABASE_URL", "postgresql://day6:day6_local_only@127.0.0.1:55433/day6_lab")
    embedder = MyEmbedder(model_name="text-embedding-3-small")
    store = PgVectorStore(database_url=db_url, dimensions=embedder.dimensions)
    store.create_schema()

    # 3. Đọc dữ liệu PDF
    pages = load_pdf(pdf_path, document_id="luat-34-2018-qh14", source="data/34-2018-qh14..pdf")

    # 4. Tạo chunks cho Chiến lược A & B
    chunks_a = []
    chunks_b = []
    for p in pages:
        chunks_a.extend(fixed_size(p, size=500, overlap=50))
        chunks_b.extend(by_paragraph(p, max_size=800))

    print(f"Tổng số chunks: Chiến lược A = {len(chunks_a)} | Chiến lược B/C = {len(chunks_b)}")

    # 5. Ingestion & Embedding
    print("\n--- Đang tạo Embedding & Upsert Chiến lược A ---")
    vecs_a = embedder.embed_documents([c.text for c in chunks_a])
    store.upsert(strategy="A", chunks=chunks_a, vectors=vecs_a)

    print("\n--- Đang tạo Embedding & Upsert Chiến lược B & C ---")
    vecs_b = embedder.embed_documents([c.text for c in chunks_b])
    store.upsert(strategy="B", chunks=chunks_b, vectors=vecs_b)

    # 6. Đọc bộ câu hỏi Benchmark
    with open(benchmark_path, "r", encoding="utf-8") as f:
        questions = json.load(f)

    # 7. Chạy Benchmark cho 3 Chiến lược
    for strat in ["A", "B", "C"]:
        t0 = time.time()
        traces = []
        for q in questions:
            q_vec = embedder.embed_query(q["question"])
            # Cấu hình C: áp dụng metadata filter khi câu hỏi có filter
            flt = q.get("filter") if strat == "C" else None
            # Chiến lược C dùng chung index B
            db_strat = "B" if strat == "C" else strat
            hits = store.search(strategy=db_strat, query_vector=q_vec, top_k=3, filters=flt)
            trace = evaluate_query(q, hits)
            traces.append(trace)

        elapsed = round(time.time() - t0, 2)
        summary = summarize(traces)

        # Lưu trace kết quả ra file JSON
        out_file = results_dir / f"trace_strategy_{strat}.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump({"summary": summary, "traces": traces}, f, ensure_ascii=False, indent=2)

        print(f"\n================ CHIẾN LƯỢC {strat} ================")
        print(f"Thời gian: {elapsed}s | Số chunks: {len(chunks_a) if strat == 'A' else len(chunks_b)}")
        print(f"DEV  - Hit@1: {summary['dev']['hit1']}/{summary['dev']['total']} ({summary['dev']['hit1_rate']*100:.1f}%) | Hit@3: {summary['dev']['hit3']}/{summary['dev']['total']} ({summary['dev']['hit3_rate']*100:.1f}%)")
        print(f"TEST - Hit@1: {summary['test']['hit1']}/{summary['test']['total']} ({summary['test']['hit1_rate']*100:.1f}%) | Hit@3: {summary['test']['hit3']}/{summary['test']['total']} ({summary['test']['hit3_rate']*100:.1f}%)")


if __name__ == "__main__":
    main()