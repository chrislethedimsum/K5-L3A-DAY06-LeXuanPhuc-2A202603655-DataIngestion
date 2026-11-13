# Benchmark Tri Thức: Luật Giáo Dục Đại Học (Luật số 34/2018/QH14)

Bộ câu hỏi benchmark được xây dựng để đánh giá hiệu quả retrieval của các chiến lược Ingestion theo [BENCHMARK.md](../BENCHMARK.md).

## 1. Tổng quan bộ câu hỏi

- **Corpus:** `data/34-2018-qh14..pdf` (35 trang nội dung thực tế, ~81.638 ký tự).
- **Tổng số câu hỏi:** 20 câu.
- **Phân chia split:**
  - **Dev:** 15 câu (`q01` – `q15`) dùng để thử nghiệm và lựa chọn cấu hình.
  - **Test:** 5 câu (`q16` – `q20`) giữ độc lập, chỉ chạy đánh giá cuối cùng.
- **Phân loại câu hỏi:**
  - Trực tiếp (`truc_tiep`): 10 câu
  - Diễn đạt lại (`dien_dat_lai`): 3 câu
  - Điều kiện / Ngoại lệ (`dieu_kien_ngoai_le`): 4 câu
  - Kiểm tra Metadata Filter (`metadata_filter`): 3 câu (2 câu ở Dev: `q06`, `q11`; 1 câu ở Test: `q17`).

## 2. Danh sách 20 câu hỏi

| ID | Split | Loại câu | Chủ đề (`section`) | Trang Gold | Tóm tắt câu hỏi | Có Filter? |
|---|---|---|---|:---:|---|:---:|
| `q01` | dev | truc_tiep | `he_thong_co_so_gd` | 1 | Định nghĩa trường đại học / học viện | Không |
| `q02` | dev | truc_tiep | `he_thong_co_so_gd` | 3 | Các hình thức đào tạo cấp văn bằng | Không |
| `q03` | dev | truc_tiep | `to_chuc_quan_tri` | 7 | Hội đồng trường ĐH công lập đại diện cho ai | Không |
| `q04` | dev | dieu_kien_ngoai_le | `to_chuc_quan_tri` | 17 | Tiêu chuẩn Hiệu trưởng cơ sở GDĐH | Không |
| `q05` | dev | truc_tiep | `quyen_tu_chu` | 19 | Quyền tự chủ và trách nhiệm giải trình | Không |
| `q06` | dev | metadata_filter | `quyen_tu_chu` | 20 | Điều kiện tiên quyết để thực hiện quyền tự chủ | **Có (`quyen_tu_chu`)** |
| `q07` | dev | dieu_kien_ngoai_le | `hoat_dong_dao_tao` | 21 | Điều kiện tự chủ mở ngành đào tạo đại học | Không |
| `q08` | dev | dien_dat_lai | `hoat_dong_dao_tao` | 22 | Căn cứ xác định chỉ tiêu tuyển sinh | Không |
| `q09` | dev | truc_tiep | `hoat_dong_dao_tao` | 24 | Hệ thống văn bằng giáo dục đại học | Không |
| `q10` | dev | dieu_kien_ngoai_le | `hoat_dong_dao_tao` | 24 | Lĩnh vực bị cấm liên kết đào tạo | Không |
| `q11` | dev | metadata_filter | `hoat_dong_dao_tao` | 25 | Liên kết đào tạo có hình thành pháp nhân mới | **Có (`hoat_dong_dao_tao`)** |
| `q12` | dev | truc_tiep | `kiem_dinh_chat_luong` | 27 | Nguyên tắc kiểm định chất lượng GDĐH | Không |
| `q13` | dev | dien_dat_lai | `kiem_dinh_chat_luong` | 27 | Mục tiêu kiểm định chất lượng GDĐH | Không |
| `q14` | dev | truc_tiep | `giang_vien_nguoi_hoc` | 29 | Các chức danh giảng viên | Không |
| `q15` | dev | dieu_kien_ngoai_le | `giang_vien_nguoi_hoc` | 29 | Trình độ chuẩn tối thiểu của giảng viên | Không |
| `q16` | test | truc_tiep | `tai_chinh_tai_san` | 30 | Nguồn tài chính của cơ sở GDĐH | Không |
| `q17` | test | metadata_filter | `tai_chinh_tai_san` | 31 | Định nghĩa học phí | **Có (`tai_chinh_tai_san`)** |
| `q18` | test | dieu_kien_ngoai_le | `tai_chinh_tai_san` | 31 | Điều kiện trường công lập tự chủ định mức học phí | Không |
| `q19` | test | truc_tiep | `dieu_khoan_thi_hanh` | 35 | Ngày có hiệu lực của Luật 34/2018/QH14 | Không |
| `q20` | test | dien_dat_lai | `to_chuc_quan_tri` | 11 | Khái niệm nhà đầu tư trường đại học tư thục | Không |

Tất cả các trích dẫn bằng chứng (`evidence_quote`) đã được kiểm chứng khớp 100% với nội dung trang tương ứng trong file `data/34-2018-qh14..pdf`.
