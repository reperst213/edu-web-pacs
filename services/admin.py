"""관리자 기능 (FR-08). 담당: 팀원 1 · 기한 12/8.

배정(T1)·재배정(T7)·재오픈(T6)은 내부에서 review.transition()을 호출한다.
status 필드를 직접 쓰지 않는다 (계획서 18.3).
"""
from services.types import Actor, Role


def assign(actor: Actor, case_id: str, reviewer_uid: str, reason: str = "") -> int:
    """반환: 새 version."""
    raise NotImplementedError("팀원 1 · 12/8")


def reopen(actor: Actor, case_id: str, reason: str) -> int:
    raise NotImplementedError("팀원 1 · 12/8")


def set_role(actor: Actor, uid: str, role: Role) -> None:
    raise NotImplementedError("팀원 1 · 12/8")
