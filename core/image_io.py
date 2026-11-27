"""영상 파일 읽기·검사·RGB 변환·처리용 사본 (FR-02). 담당: 팀원 2 · 기한 12/4.

규칙 (계획서 1장, 18.4):
- 지원 형식: 피부경 컬러 DICOM, PNG/JPEG (8-bit, 10 MiB·1,200만 픽셀 이하)
- 반환 배열은 항상 RGB uint8 (H, W, 3). YBR DICOM은 RGB로 변환한다.
- 처리용 사본은 긴 변 1,024px.
- 잘못된 파일은 services.errors.ValidationError(사유)로 거부한다.
"""
MAX_BYTES = 10 * 1024 * 1024
MAX_PIXELS = 12_000_000
PREVIEW_LONG_SIDE = 1024


def read_image(data: bytes, filename: str):
    """반환: (RGB 배열, 메타데이터 dict)."""
    raise NotImplementedError("팀원 2 · 12/4")


def make_preview(rgb):
    """반환: 긴 변 1,024px로 줄인 RGB 배열 (이미 작으면 그대로)."""
    raise NotImplementedError("팀원 2 · 12/4")
