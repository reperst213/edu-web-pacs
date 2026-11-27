"""파일 저장 규칙 (계획서 6.2, 6.3). 담당: 팀원 2 · 기한 12/4.

DATA_DIR 아래:
  originals/{image_id}.{dcm,png,jpg}  원본, 한 번 쓰고 덮어쓰기 금지
  previews/{image_id}.png             긴 변 1,024px 처리용 사본
  results/{run_id}.png                처리 결과
  features/                           특징 행렬 (팀원 4)
  tmp/, orphans/                      쓰기 중 파일, DB 누락 파일
"""
import os
from pathlib import Path


def data_dir() -> Path:
    return Path(os.getenv("DATA_DIR", "./data_local"))


def save_original(image_id: str, ext: str, data: bytes) -> Path:
    """tmp에 쓴 뒤 originals로 원자적 이동. 이미 있으면 덮어쓰지 않는다."""
    raise NotImplementedError("팀원 2 · 12/4")


def move_to_orphans(path: Path) -> Path:
    """DB 쓰기가 실패한 파일을 orphans/로 옮긴다."""
    raise NotImplementedError("팀원 2 · 12/4")
