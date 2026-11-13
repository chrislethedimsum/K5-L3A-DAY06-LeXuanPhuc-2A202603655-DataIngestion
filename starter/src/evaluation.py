"""Evaluate retrieved evidence and preserve per-query traces."""
import re
from typing import Any


def _norm(s: str) -> str:
    return re.sub(r'\s+', ' ', s).strip().lower()


def evaluate_query(question: dict[str, Any], hits: list[dict[str, Any]]) -> dict[str, Any]:
    """Kiểm tra xem top hits có chứa đúng gold_page và evidence_quote không."""
    gold_page = question["gold_page"]
    gold_quote = _norm(question["evidence_quote"])
    hit_rank = None

    for rank, h in enumerate(hits, start=1):
        h_text = _norm(h["text"])
        # Kiểm tra đúng trang và text chunk có chứa trích dẫn bằng chứng
        if h["page"] == gold_page and gold_quote in h_text:
            hit_rank = rank
            break

    hit_1 = (hit_rank == 1)
    hit_3 = (hit_rank is not None and hit_rank <= 3)

    return {
        "id": question["id"],
        "split": question["split"],
        "type": question.get("type", "unknown"),
        "question": question["question"],
        "gold_page": gold_page,
        "evidence_quote": question["evidence_quote"],
        "filter": question.get("filter"),
        "hit_rank": hit_rank,
        "hit_at_1": hit_1,
        "hit_at_3": hit_3,
        "top_hits": hits
    }


def summarize(traces: list[dict[str, Any]]) -> dict[str, Any]:
    """Tổng hợp chỉ số Hit@1 và Hit@3 cho toàn bộ và tách riêng dev/test."""
    def _calc(items: list[dict[str, Any]]) -> dict[str, Any]:
        total = len(items)
        if total == 0:
            return {"total": 0, "hit1": 0, "hit1_rate": 0.0, "hit3": 0, "hit3_rate": 0.0}
        h1 = sum(1 for x in items if x["hit_at_1"])
        h3 = sum(1 for x in items if x["hit_at_3"])
        return {
            "total": total,
            "hit1": h1,
            "hit1_rate": round(h1 / total, 4),
            "hit3": h3,
            "hit3_rate": round(h3 / total, 4)
        }

    dev_items = [t for t in traces if t["split"] == "dev"]
    test_items = [t for t in traces if t["split"] == "test"]

    return {
        "all": _calc(traces),
        "dev": _calc(dev_items),
        "test": _calc(test_items)
    }