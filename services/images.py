"""영상 등록·조회 (FR-02). 담당: 팀원 2 · 기한 12/4.

저장 순서는 계획서 6.3을 따른다: tmp → 검사 → SHA-256 중복 확인 → originals → Firestore.
"""
from services.types import Actor


def upload_image(actor: Actor, case_id: str, filename: str, data: bytes) -> str:
    """반환: image_id (IMG- + SHA-256 앞 12자리)."""
    raise NotImplementedError("팀원 2 · 12/4")


def load_preview(actor: Actor, image_id: str):
    """반환: 처리용 사본, RGB uint8 (H, W, 3), 긴 변 1,024px."""
    raise NotImplementedError("팀원 2 · 12/4")


def get_tags(actor: Actor, image_id: str) -> dict:
    """반환: 화면에 보여줄 DICOM 태그 (PNG/JPEG는 파일 정보)."""
    raise NotImplementedError("팀원 2 · 12/4")
