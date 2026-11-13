# Báo cáo cá nhân — Day 6

- Họ và tên: Lê Xuân Phúc
- MSSV: 2A202603655
- Lớp: K5-L3A
- Chủ đề và corpus: Luật sửa đổi, bổ sung một số điều của Luật Giáo dục đại học (Luật số 34/2018/QH14), Công báo Nước CHXHCNVN số 1135+1136, 35 trang nội dung thực tế.
- Repo bài nộp: K5-L3A-DAY06-LeXuanPhuc-2A202603655-DataIngestion

## Dữ liệu và pipeline

- Chủ đề, nguồn/quyền, số trang và quy tắc tính trang:
  - Chủ đề: Văn bản quy phạm pháp luật - Luật sửa đổi, bổ sung một số điều của Luật Giáo dục đại học (Luật số 34/2018/QH14).
  - Nguồn/quyền: https://vanban.chinhphu.vn/he-thong-van-ban?classid=1&mode=1&typegroupid=3, Căn cứ vào điều 19 luật sở hữu trí tuệ Việt Nam thì văn bản quy phạm pháp luật không thuộc đối tượng bảo hộ quyền tác giả mà thuộc phạm vi công cộng, được phép khai thác, xử lý và trích dẫn công khai.
- Chuẩn hóa, lỗi và giới hạn:
  - Chuẩn hóa: Chuyển đổi mã Unicode NFC, loại bỏ header/footer lặp của Công báo và thu gọn nhiều khoảng trắng thừa về khoảng trắng đơn.
  - Lỗi: Khắc phục và xử lí lỗi kerning ngắt âm tiết đặc thù của PDF công báo như c ơ s ở thành cơ sở bằng regex hợp nhất phụ âm - nguyên âm tiếng Việt.
  - Giới hạn: Dùng bộ bóc tách pypdf đọc văn bản tuần tự nó sẽ không dựng lại cấu trúc bảng biểu phức tạp. Mà một số điều khoản rất dài vượt quá ngưỡng max_size vẫn buộc phải ngắt mảnh.
- Embedding model/provider/version/số chiều, vector store/version, metric, lệnh chạy và chi phí:
  - Embedding model: OpenAI text-emdedding-3-small gọi qua OpenAI API chính thức. Giữ nguyên 100% model và số chiều cho cả 3 chiến lược.
  - Vector store: Dùng PostgreSQL 16 + pgvector (0.7.0+) được triển khai qua Docker Compose trên cổng 127.0.0.1:55433.
  - Metric: Cosine distance do sử dụng toán tử <=> của pgvector, quy đổi similarity score bừang công thức 1 - (embedding <=> query_vector).
  - Lệnh chạy: `cd starter
docker-compose -p day6_student_starter up -d
python -m src.run`
  - Chí phí: Tổng dung lượng văn bản ~81638 ký tự ~(25000 tokens embedding văn bản) + 20 câu hỏi query (~1000 tokens) = ~$0.0005 USD.
- Metadata bắt buộc, trường lọc bổ sung, nguồn giá trị và lý do chọn:
  - Metadata bắt buộc: document_id (luat-34-2018-qh14), source (data/34-2018-qh14..pdf), page (số trang vật lý 1-35)
  - Trường hợp bổ sung: section gồm 8 nhóm chính (he_thong_co_so_gd, to_chuc_quan_tri, quyen_tu_chu, hoat_dong_dao_tao, kiem_dinh_chat_luong, giang_vien_nguoi_hoc, tai_chinh_tai_san, dieu_khoan_thi_hanh).
  - Nguồn giá trị & Lí do chọn: Được xác định chính xác theo dải trang và nhóm điều khoản trong luật. Trường này có giá trị cực lớn để khoanh vùng tìm kiếm ví dụ khi tra cứu về học phí thì giới hạn trong tai_chinh_tai_san, triệt tiêu các chun nhiễu từ các chương khác có từ khóa tương tự.

## Cấu hình và benchmark

- A / B / C (tham số cụ thể, khác biệt duy nhất B–C):
  - A (Fixed-size): Cửa số trượt kích thước cố định 500 ký tự, overlap 50 ký tự; gắn metadata chuẩn; không dùng bộ lọc.
  - B (Structure-aware Paragraph): Cắt theo ranh giới tự nhiêu của điều khoản luật như các mốc Điều 1, Khoản 1., 2. , điểm (a,b), giới hạn max_size = 800 ký tự. Cũng gắn cùng metadata và không dùng bộ lọc.
  - C (Paragraph + Metadata Filter): Tái sử dụng 100% cấu trúc chunk của Chiến lược B, nhưng áp dụng Metadata Filter theo trường section khi câu hỏi có yêu cầu ngữ cảnh lọc.
  - So sánh B và C: Tuy B và C cùng chung corpus, chung embedding model, chung vector store, chung các đoạn chunk, nhưng điểm khác biệt duy nhất là việc kích hoạt metadata filter tại thời điểm query.
- ≥20 câu: phân chia ≥15 dev / ≥5 test, câu metadata filter và cách kiểm chứng evidence:
  - Bộ benchmark gồm 20 câu hỏi, tách cố định thành 15 câu DEV từ q01-q15 và 5 câu Test từ q16-q20.
  - Phủ đủ 4 nhóm câu hỏi bao gồm trực tiếp (10 câu), diễn đạt lại (3 câu), ngoại lệ/điều kiện (4 câu) và kiểm tra metadata filter (3 câu q06,q11 còn dev thì q17).
    Kiểm chứng evidence: 100% câu hỏi đều có evidence_quote được đối soát ký tự trực tiếp trên trang PDF đã chuẩn hóa, đảm bảo trích dẫn tồn tại thực tế và hỗ trợ đầy đủ cho expected_answer.
- Tiêu chí chọn chiến lược đã chốt trước khi xem test:
  - Tiêu chí ưu tiên 1: Đạt số Evidence Hit@3 và Hit@1 cao nhất trên tập Dev.
  - Tiêu chí ưu tiên 2: Tính toàn vẹn ngữ nghĩa của chunk >= 1.5/2.
  - Tiêu chí ưu tiên 3: Khả năng loại bỏ nhiễu ngoài phạm vi chuyên môn thông qua Metadata Filtering.

## Kết quả

Bảng 1: Kết quả truy xuất và tài nguyên
| Strategy | Split | Hit@1 (n/N) | Evidence Hit@3 (n/N) | Chunk count | Thời gian | Chi phí |
| --- | --- | :---: | :---: | :---: | :---: | :---: |
| A | Dev | 6/15 (40.0%) | 6/15 (40.0%) | 175 | 1.85s | ~$0.0003 |
| A | Test | 0/5 (0.0%) | 1/5 (20.0%) | 175 | 0.58s | ~$0.0001 |
| B | Dev | 9/15 (60.0%) | 11/15 (73.3%) | 110 | 1.82s | ~$0.0002 |
| B | Test | 2/5 (40.0%) | 3/5 (60.0%) | 110 | 0.56s | ~$0.0001 |
| C | Dev | 9/15 (60.0%) | 11/15 (73.3%) | 110 | 1.84s | ~$0.0002 |
| C | Test | 2/5 (40.0%) | 3/5 (60.0%) | 110 | 0.57s | ~$0.0001 |

Bảng 2 Đánh giá chất lượng 5 khía cạnh
| Strategy | Coherence trung bình /2 (n=10) | Metadata đủ và đúng (n/N) | Filter tuân thủ (n/N hoặc N/A) | Grounding 0/1/2 (số câu) và trung bình /2 (n=5 test) |
| --- | :---: | :---: | :---: | :---: |
| A | 0.9 / 2.0 | 15/15 (100%) | N/A | [4 câu mức 0, 0 câu mức 1, 1 câu mức 2] → **0.4 / 2.0** |
| B | 2.0 / 2.0 | 15/15 (100%) | N/A | [1 câu mức 0, 1 câu mức 1, 3 câu mức 2] → **1.4 / 2.0** |
| C | 2.0 / 2.0 | 15/15 (100%) | 3/3 (100%) | [1 câu mức 0, 1 câu mức 1, 3 câu mức 2] → **1.4 / 2.0** |

Đường dẫn trace, nhãn thủ công và cách chọn mẫu:

- File trace chi tiết được lưu lại [results/trace_strategy_A.json](results/trace_strategy_A.json), [results/trace_strategy_B.json](results/trace_strategy_B.json), [results/trace_strategy_C.json](results/trace_strategy_C.json).
- Mẫu Cohenrence được chọn cố định tại 10 ví trị điều khoản quan trọng trải dài từ trang 1 đến 24 (Điều 4,6,14,16,16a,20,32,33,34,38).
- Mẫu Grounding và Metadata được audit thủ công trên toàn bộ 5 câu hỏi của tập Test (q16 đến q20).

## Phân tích và kết luận

- So sánh A–B và B–C; 2 ví dụ sai có ID câu và nguồn:
  - Chunking A vs B:
    - Chiến lược A với fixed_size = 500 gặp hiện tượng nghiệm trọng là cắt rách câu văn và điều khoản luật. Việc cắt cứng ngắc theo số ký tự làm mất chủ ngữ, đứt mạch logic khiến coherence chỉ đạt 0.9/2 -> Evidence Hit@3 trên tập Dev chỉ đạt 40% và rớt còn 20% ở tập Test khi bằng chứng bị chia làm 2 nửa nằm ở 2 chunk khác nhau.
    - Còn với B by_paragraph = 800 giưu trọn vẹn ngữ cảnh của từng khoản luật. Độ mạch lạc đạt điểm tuyệt đối đa 2.0/2.0 giúp vector embedding nắm bắt trọn vẹn ngữ nghĩa, đưa Evidence Hit@3 tăng lên 73.3% ở Dev và 60.0% ở Test.
  - Metadata filtering B vs C:
    - Trên câu hỏi q06 (Điều kiện tự chủ có filter section: "quyen_tu_chu") thì ở chiến lược B: Top-3 chunk trả về chứa ['quyen-tu-chu','dieu_khoan_thi_hanh','quyen_tu_chu'] -> Rank 2 bị nhiễm một chunk từ phần Điều khoản thi hành do có nhắc đến cụm từ 'quyền tự chủ'.
    - Còn với C nhờ áp dụng filter metadata, Top-3 chunk trả về 100% thuộcc phân hệ quyen_tu_chu. Bộ lọc đã loại bỏ triệt để chunk nhiễu ngoài phạm vi mà không làm suy giảm tốc độ truy vấn.
  - Phân tích 2 failure cases cụ thể:
    - Câu q16 (Test, Trang 30, Chủ đề tai_chinh_tai_san)
      - Câu hỏi: Nguồn tài chính của cơ sở giáo dục đại học bao gồm những khoản thu chủ yếu nào?
      - Nguyên nhân thất bại: Do khoản 1 điều 64 liệt kê 4 điểm a,b,c,d rất dài và dài hơn max_size khiến bị tách thành 2 chunk. Chunk top-1 trả về chỉ chứa điểm c và d gồm thu từ dịch vụ và đầu tư, trong khi bằng chứng cột lõi lại ở chunk liền trước (điểm a về học phí) -> hệ thống không đạt evidence hit với đánh giá grounding chỉ đạt mức 1/2.
      - Bài học: Cần cơ chế gom nhóm ngữ cảnh hoặc ử dụng chunk cha-con (Parent Document Retrieval) khi xử lí các điều khoản liệt kê dài.
    - Câu q20 (Test, Trang 11, Chủ đề to_chuc_quan_tri)
      - Câu hỏi: Ai được coi là nhà đầu tư thành lập trường đại học tư thục theo quy định của Luật?
      - Nguyên nhân: Do cả hai rank 1 và 2 đều trả về trang 12 Khoản 2 điều 16a về quyền hạn của nhà đầu tư thay vì trang 11 khoản 1 điều 16a định nghĩa nhà đầu tư. Do câu query có cụm "đầu tư thành lập trường đại học tư thục", mô hình embedding bị thu hút mạnh bởi đoạn văn ở trang 12 có chứa nguyên văn cụm "đầu tư thành lập cơ sở giáo dục đại học tư thục".
      - Bài học: Mô hình dense embedding thuần túy dễ bị nhầm lẫn giữa định nghĩa đối tượng và quyền hạn đối tượng nếu hai đoạn dùng chung từ vưng chuyên ngành.
- Chiến lược chọn, đánh đổi, điều kiện áp dụng:
  - Chiến lược chọn: C (Structure-aware Chunking kết hợp với Metadata filtering) là tối ưu nhất.
  - Đánh đổi:
    - Do B & C cần logic phân tích cấu trúc phức tạp và phụ thuộc vào định dạng văn bản nguồn.
    - Chiến lược C đòi hỏi câu hỏi hoặc ứng dụng đầu cuối phải cung cấp được thông tin ngữ cảnh (section) trước khi truy xuất.
  - Điều kiện áp dụng: Rất phù hợp cho hệ thống tra cứu văn bản pháp luật, tài liệu kỹ thuật, chính sách quy chế nội bộ - nơi văn bản có cấu trúc phân tầng rõ ràng và người dùng thường tìm kiếm theo chuyên mục cụ thể.
- Hạn chế của dữ liệu, nhãn, test nhỏ, đo thời gian/chi phí:
  - Tập test gồm 5 câu là kích thước mẫu nhỏ, mang tính chất minh họa phương pháp luận hơn là kiểm định thống kê lướn.
  - Metadata section hiện được gãn tĩnh theo dải trang PDF; tại các trang chuyển giao giữa 2 điều khoản có thể xuát hiện lệch phân loại nhẹ.
  - Metric đánh giá substring exact-match đối với evidence có phần khắt khe nếu chunk thiếu một vài từ phụ nhưng vẫn đủ thông tin trả lời.
- Nếu làm lại hoặc mở rộng, cải tiến gì?
  - Parent-child chunking: lưu trữ chunk nhỏ để embedding chính xcas nhưng trả về chunk cha như toàn bộ Điều luật để LLM có trọn vẹn ngữ cảnh trả lời, sẽ giải quyết vấn đề của q16.
  - Hybrid search: kết hợp dense vector sẻach (text-embedding-3-small) với sparese keyword search (bm25) để tăng cường độ chính xác cho các câu hỏi tra cứu định nghĩa hoặc ngoại lệ (như câu q20).
  - Cuối cùng là metadata granualarity: trích xuất metadata tự động ở cấp độ Điều luật (article_id) thay vì cấp độ trang.
