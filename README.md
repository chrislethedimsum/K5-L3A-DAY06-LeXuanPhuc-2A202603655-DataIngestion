# Day 06 · Data Ingestion Engineering

**Học viên:** Lê Xuân Phúc — **MSSV:** 2A202603655 — **Lớp:** K5-L3A  
**Báo cáo cá nhân:** [report/individual/2A202603655_LeXuanPhuc.md](report/individual/2A202603655_LeXuanPhuc.md)  
**Corpus dữ liệu:** [data/34-2018-qh14..pdf](data/34-2018-qh14..pdf) | **Manifest:** [data/manifest.json](data/manifest.json)  
**Bộ Benchmark:** [benchmark/questions.json](benchmark/questions.json) | **Log thí nghiệm:** [artifacts/experiment_log.csv](artifacts/experiment_log.csv)  
**Web UI Demo:** [demo/index.html](demo/index.html) | [demo/server.py](demo/server.py)

---

## 🖥️ Hướng Dẫn Khởi Chạy & Sử Dụng Web UI Demo

Dự án cung cấp giao diện Web tương tác hiện đại tại thư mục `demo/` giúp trực quan hóa toàn bộ pipeline Ingestion, so sánh 3 chiến lược và tra cứu tri thức với trợ lý giải thích có trích dẫn nguồn.

### 1. Cách khởi chạy giao diện Demo

Bạn có thể chạy UI theo **1 trong 2 cách** sau:

#### Cách 1: Chạy qua Server Python (Khuyên Dùng)
Từ thư mục gốc của project, chạy lệnh:
```bash
python demo/server.py
```
👉 Trình duyệt sẽ tự động mở tại địa chỉ: **`http://localhost:8000`** *(nếu cổng 8000 bận, server sẽ tự động chuyển sang 8080)*.

#### Cách 2: Mở trực tiếp file HTML (Không cần server)
Nhấp đúp chuột trực tiếp vào file **`demo/index.html`** hoặc mở bằng bất kỳ trình duyệt nào (Chrome, Safari, Edge, Firefox). Toàn bộ dữ liệu benchmark, corpus và kết quả trace đã được đóng gói độc lập trong `demo/data.js`, cho phép chạy mượt mà ngay cả khi offline.

---

### 2. Hướng dẫn các tính năng trên giao diện UI

Giao diện gồm **4 tab chức năng chính**:

1. **🔍 Tra Cứu & Trợ Lý Giải Thích (Live Search & Grounded Explanation):**
   - **Ô tìm kiếm:** Nhập câu hỏi pháp lý bất kỳ (ví dụ: *"Trường đại học công lập nào được tự chủ học phí?"*) hoặc bấm vào các câu hỏi mẫu có sẵn.
   - **Tùy chọn chiến lược:** Chuyển đổi giữa Chiến lược A (Fixed 500c), B (Paragraph 800c) hoặc C (Paragraph + Filter).
   - **Lọc theo Phân hệ (Section):** Khoanh vùng tìm kiếm trong 8 phân hệ chuyên môn (`quyen_tu_chu`, `tai_chinh_tai_san`, `hoat_dong_dao_tao`...).
   - **Câu trả lời trực diện (Direct Answer):** Trả lời ngắn gọn, đúng trọng tâm câu hỏi.
   - **Diễn giải quy định & điều kiện:** Phân tích chi tiết quy định pháp luật và điều kiện áp dụng.
   - **Căn cứ pháp lý & Nguồn trích dẫn (Verified Citation):** Chỉ rõ **Trang PDF số mấy**, **Phân hệ nào** trong Luật số 34/2018/QH14 kèm **nguyên văn đoạn trích bằng chứng (Evidence Quote)**.
   - **Top 3 Chunks truy xuất:** Hiển thị 3 đoạn trích tương quan cao nhất kèm điểm số Similarity Score (%), Chunk ID, nhãn trang và phân hệ.

2. **📊 So Sánh 3 Chiến Lược (Dashboard & Analytics):**
   - Bảng tổng hợp đối chiếu chỉ số `Hit@1`, `Hit@3` trên tập Dev (15 câu) và Test (5 câu).
   - Đánh giá chất lượng 5 khía cạnh: Điểm Coherence (tính mạch lạc), Grounding (độ đầy đủ bằng chứng), độ hữu dụng của Metadata và tỷ lệ tuân thủ Filter.
   - Phân tích 2 trường hợp lỗi thực tế (`q16` và `q20`) kèm bài học rút ra.

3. **📑 20 Câu Hỏi Benchmark & Traces:**
   - Xem toàn bộ danh sách 20 câu hỏi benchmark chuẩn hóa.
   - Bộ lọc xem theo tập: Tất cả (20), Dev (15), Test (5), hoặc các câu có Filter (3).
   - Bấm vào từng câu hỏi để xem chi tiết đáp án kỳ vọng, bằng chứng Gold và **bảng đối chiếu thứ hạng rank truy xuất của Chiến lược A vs B vs C**.

4. **📚 Corpus & Phân Hệ Metadata:**
   - Xem thông tin khai báo Manifest (35 trang nội dung, 81.638 ký tự, giấy phép khai thác).
   - Khám phá 8 phân hệ metadata (`section`) kèm dải trang và danh sách các điều khoản luật bao phủ.

---

## ⚡ Hướng Dẫn Setup & Chạy Tái Lập Pipeline (Quickstart)

```bash
# 1. Kích hoạt môi trường và cài đặt dependencies
cd starter
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install openai

# 2. Cấu hình biến môi trường
cp .env.example .env
# Điền OPENAI_API_KEY và EMBEDDING_MODEL=text-embedding-3-small vào .env

# 3. Khởi chạy PostgreSQL + pgvector qua Docker
docker-compose -p day6_student_starter up -d --wait

# 4. Chạy toàn bộ pipeline và benchmark 3 chiến lược
python -m src.run
```
Kết quả trace và thống kê sẽ được tự động xuất ra thư mục `results/` và `starter/results/`.

---

## 📊 Kết Quả Thực Nghiệm Tổng Hợp

| Chiến lược | Phương pháp Chunking | Metadata Filter | Dev Hit@1 ($n/15$) | Dev Hit@3 ($n/15$) | Test Hit@1 ($n/5$) | Test Hit@3 ($n/5$) | Coherence (/2) | Grounding Test (/2) |
|---|---|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **A** | Fixed-size 500c (overlap 50) | None | 6/15 (40.0%) | 6/15 (40.0%) | 0/5 (0.0%) | 1/5 (20.0%) | 0.9 / 2.0 | 0.4 / 2.0 |
| **B** | Paragraph 800c (Khoản luật) | None | **9/15 (60.0%)** | **11/15 (73.3%)** | **2/5 (40.0%)** | **3/5 (60.0%)** | **2.0 / 2.0** | **1.4 / 2.0** |
| **C** | Paragraph 800c (Giống B) | Section Filter | **9/15 (60.0%)** | **11/15 (73.3%)** | **2/5 (40.0%)** | **3/5 (60.0%)** | **2.0 / 2.0** | **1.4 / 2.0** |

> **Kết luận:** Chiến lược C (Structure-aware Paragraph kết hợp Metadata Filtering) là cấu hình tối ưu nhất: vượt trội về tính mạch lạc ngữ nghĩa, đạt Hit@3 cao nhất (73.3% ở Dev) và triệt tiêu 100% chunk nhiễu ngoài phân hệ khi truy vấn có điều kiện lọc.

---

## 📁 Cấu Trúc Thư Mục Dự Án

```text
├── STUDENT.md                              # Thông tin học viên và commit chốt bài
├── README.md                               # Hướng dẫn setup, chạy tái lập và hướng dẫn UI
├── data/
│   ├── 34-2018-qh14..pdf                   # File PDF corpus gốc (35 trang nội dung hữu ích)
│   └── manifest.json                       # Khai báo bản quyền, nguồn, số trang, 8 phân hệ section
├── benchmark/
│   ├── questions.json                      # 20 câu hỏi benchmark (15 Dev, 5 Test, 3 câu Filter)
│   └── README.md                           # Bảng mô tả chi tiết bộ câu hỏi benchmark
├── artifacts/
│   └── experiment_log.csv                  # Nhật ký thí nghiệm và giả thuyết 3 chiến lược A/B/C
├── results/
│   ├── trace_strategy_A.json               # Trace chi tiết kết quả truy xuất Chiến lược A
│   ├── trace_strategy_B.json               # Trace chi tiết kết quả truy xuất Chiến lược B
│   └── trace_strategy_C.json               # Trace chi tiết kết quả truy xuất Chiến lược C
├── report/
│   └── individual/
│       └── 2A202603655_LeXuanPhuc.md       # Báo cáo cá nhân hoàn chỉnh theo rubric
├── demo/
│   ├── index.html                          # Giao diện Web UI Demo trực quan
│   ├── data.js                             # Dữ liệu độc lập phục vụ UI
│   └── server.py                           # Local server một dòng lệnh để chạy demo
└── starter/
    ├── docker-compose.yml                  # PostgreSQL 16 + pgvector container
    ├── requirements.txt                    # Danh sách thư viện Python
    └── src/                                # Toàn bộ mã nguồn Ingestion Pipeline
        ├── ingestion.py                    # Bóc tách PDF và chuẩn hóa âm tiết tiếng Việt
        ├── chunking.py                     # Thực hiện 3 chiến lược chunking
        ├── embeddings.py                   # Tích hợp OpenAI text-embedding-3-small
        ├── store.py                        # Quản lý pgvector, lưu trữ và tìm kiếm Cosine
        ├── evaluation.py                   # Tính toán chỉ số Hit@1 và Hit@3
        └── run.py                          # Điều phối chạy toàn bộ pipeline
```

---

## 📚 Tài Liệu Hướng Dẫn Của Đề Bài

| Bạn cần tìm | Tài liệu |
|---|---|
| Báo cáo cá nhân | [report/individual/2A202603655_LeXuanPhuc.md](report/individual/2A202603655_LeXuanPhuc.md) |
| Setup baseline PostgreSQL + pgvector | [starter/README.md](starter/README.md) |
| Các bước làm và cách tính chỉ số | [GUIDE.md](GUIDE.md) |
| Tiến độ trong 4 giờ | [CHECKPOINTS.md](CHECKPOINTS.md) |
| Năm tiêu chí benchmark và bộ câu hỏi | [BENCHMARK.md](BENCHMARK.md) |
| Tiêu chí chấm điểm | [RUBRIC.md](RUBRIC.md) |
| Quy tắc sử dụng dữ liệu, AI và API | [RULES.md](RULES.md) |
| Cách nộp bài | [SUBMISSION.md](SUBMISSION.md) |
