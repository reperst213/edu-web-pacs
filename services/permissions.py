"""서버 측 권한 검사 (FR-14). 담당: 팀원 1 · 기한 12/1.

action 목록과 허용 조건은 계획서 18.2 표를 따른다.
거부하면 PermissionDenied를 던지고 audit.log(..., result="deny")를 남긴다.
상태 조건(예: 검토 중일 때만)은 각 서비스에서 따로 확인한다.
"""
from services.types import Actor

ACTIONS: tuple[str, ...] = (
    "case.create", "image.upload",
    "case.update_intake",
    "case.read", "image.read",
    "case.assign", "case.reopen", "user.manage", "audit.read",
    "process.run", "note.write",
    "search.run",
    "review.start", "review.complete", "review.request_rework",
    "review.resubmit",
)


def require(actor: Actor, action: str, case: dict | None = None) -> None:
    raise NotImplementedError("팀원 1 · 12/1")
