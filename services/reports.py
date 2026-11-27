"""요약 리포트 (FR-12). 담당: 팀원 2 · 기한 12/8.

finalize()는 팀원 4의 review.transition()이 T4(검토 중 → 완료)를 처리할 때만 호출한다.
"""
from services.types import Actor


def save_draft(actor: Actor, case_id: str, findings: str,
               used_run_ids: list[str], reference_image_ids: list[str]) -> None:
    raise NotImplementedError("팀원 2 · 12/8")


def finalize(actor: Actor, case_id: str) -> None:
    raise NotImplementedError("팀원 2 · 12/8")


def get_report(actor: Actor, case_id: str) -> dict:
    raise NotImplementedError("팀원 2 · 12/8")
