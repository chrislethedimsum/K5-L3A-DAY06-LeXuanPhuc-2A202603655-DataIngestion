"""Read and normalize source data. TODO: implement functions."""
from pathlib import Path
from .models import DocumentPage
import re
import pypdf

# Ánh xạ dải trang sang phân hệ (section) phục vụ metadata filtering
PAGE_SECTION_MAP = [
    ((1, 5), "he_thong_co_so_gd"),
    ((6, 18), "to_chuc_quan_tri"),
    ((19, 21), "quyen_tu_chu"),
    ((21, 26), "hoat_dong_dao_tao"),
    ((26, 29), "kiem_dinh_chat_luong"),
    ((29, 30), "giang_vien_nguoi_hoc"),
    ((30, 33), "tai_chinh_tai_san"),
    ((33, 35), "dieu_khoan_thi_hanh"),
]

def get_section_for_page(page_num: int) -> str:
    for (start, end), sec in PAGE_SECTION_MAP:
        if start <= page_num <= end:
            return sec
    return "khac"

def normalize_text(text: str) -> str:
    """Loại bỏ header công báo và sửa lỗi ngắt âm tiết font tiếng Việt."""
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        # Bỏ dòng tiêu đề công báo và số trang công báo
        if "CÔNG BÁO" in stripped or re.match(r"^\d+\s+CÔNG BÁO", stripped):
            continue
        lines.append(stripped)
    text = " ".join(lines)
    # Nối phụ âm đầu bị tách rời nguyên âm (ví dụ: 'c ơ  s ở' -> 'cơ sở')
    text = re.sub(
        r'\b(ngh|ng|nh|ch|th|ph|kh|tr|gi|qu|[bcdđghklmnprstvxBCĐDGHIKLMNOPQRSTVX])\s+([a-zA-Zàáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵ]+)\b',
        r'\1\2',
        text
    )
    text = re.sub(
        r'\b([a-zA-Zàáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵ])\s+([àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵ]\b)',
        r'\1\2',
        text
    )
    # Thu gọn nhiều khoảng trắng thừa
    return re.sub(r'\s+', ' ', text).strip()

def load_pdf(path: Path, document_id: str, source: str) -> list[DocumentPage]:
    """Trích xuất từng trang vật lý, ghi nhận và bỏ qua trang rỗng."""
    reader = pypdf.PdfReader(str(path))
    pages: list[DocumentPage] = []
    for idx, page in enumerate(reader.pages, start=1):
        raw_text = page.extract_text() or ""
        cleaned = normalize_text(raw_text)
        if not cleaned:
            print(f"[Ingestion] Cảnh báo: Trang {idx} rỗng, đã bỏ qua.")
            continue
        sec = get_section_for_page(idx)
        pages.append(
            DocumentPage(
                document_id=document_id,
                source=source,
                page=idx,
                text=cleaned,
                metadata={"section": sec}
            )
        )
    print(f"[Ingestion] Đã nạp thành công {len(pages)} trang có nội dung từ {path.name}")
    return pages
