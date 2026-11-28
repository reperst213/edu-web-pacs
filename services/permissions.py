"""서버 측 권한 검사 (FR-14). 담당: 팀원 1 · 기한 12/1.

action 목록과 허용 조건은 계획서 18.2 표를 따른다.
거부하면 PermissionDenied를 던지고 audit.log(..., result="deny")를 남긴다.
상태 조건은 여기서도 보지만, 각 서비스에서도 따로 확인한다
(InvalidTransition/ValidationError).

- 본인 등록: case["registered_by"] == actor.uid
- 본인 배정: case["assignee_uid"] == actor.uid
"""
import logging
from typing import NamedTuple

from services import audit
from services.errors import PermissionDenied
from services.types import ROLE_LABELS, STATUS_LABELS, Actor, Status

logger = logging.getLogger(__name__)

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


class Rule(NamedTuple):
    owner: str | None = None       # None | "registered" | "assigned"
    status: Status | None = None   # 이 상태일 때만 허용


ANY = Rule()
REGISTERED = Rule(owner="registered")
ASSIGNED = Rule(owner="assigned")

# action → {역할: 조건}. 표에 없는 역할은 거부.
RULES: dict[str, dict[str, Rule]] = {
    "case.create": {"registrar": ANY, "admin": ANY},
    "image.upload": {"registrar": ANY, "admin": ANY},
    "case.update_intake": {"registrar": Rule("registered", Status.RECEIVED), "admin": ANY},
    "case.read": {"registrar": REGISTERED, "reviewer": ASSIGNED, "admin": ANY},
    "image.read": {"registrar": REGISTERED, "reviewer": ASSIGNED, "admin": ANY},
    "case.assign": {"admin": ANY},
    "case.reopen": {"admin": ANY},
    "user.manage": {"admin": ANY},
    "audit.read": {"admin": ANY},
    "process.run": {"reviewer": Rule("assigned", Status.IN_REVIEW)},
    "note.write": {"reviewer": Rule("assigned", Status.IN_REVIEW)},
    "search.run": {"reviewer": ASSIGNED, "admin": ANY},  # admin은 조회만 (선택 불가는 search 서비스에서)
    "review.start": {"reviewer": ASSIGNED},
    "review.complete": {"reviewer": ASSIGNED},
    "review.request_rework": {"reviewer": ASSIGNED},
    "review.resubmit": {"registrar": Rule("registered", Status.NEEDS_REWORK)},
}


def _deny_reason(actor: Actor, action: str, case: dict | None) -> str | None:
    """허용이면 None, 거부면 화면에 보일 한국어 사유."""
    allowed = RULES[action]
    rule = allowed.get(actor.role)
    if rule is None:
        roles = ", ".join(ROLE_LABELS[r] for r in allowed)
        return f"이 작업은 {roles}만 할 수 있습니다."
    if rule.owner is None and rule.status is None:
        return None
    if case is None:
        return "케이스 정보가 없어 권한을 확인할 수 없습니다."
    if rule.owner == "registered" and case.get("registered_by") != actor.uid:
        return "본인이 등록한 케이스만 다룰 수 있습니다."
    if rule.owner == "assigned" and case.get("assignee_uid") != actor.uid:
        return "이 케이스에 배정된 검토자만 할 수 있습니다."
    if rule.status is not None and case.get("status") != rule.status:
        need = STATUS_LABELS[rule.status]
        return f"'{need}' 상태인 케이스에서만 할 수 있습니다."
    return None


def require(actor: Actor, action: str, case: dict | None = None) -> None:
    """허용되지 않으면 PermissionDenied. 모르는 action은 ValueError (코드 오류)."""
    if action not in RULES:
        raise ValueError(f"알 수 없는 action: {action!r}")
    reason = _deny_reason(actor, action, case)
    if reason is None:
        return
    target = (case or {}).get("case_id", "")
    try:
        audit.log(actor, action, target, "deny", reason)
    except Exception:  # 기록 실패가 거부를 막으면 안 된다
        logger.exception("감사 로그 기록 실패: %s %s %s", actor.uid, action, target)
    raise PermissionDenied(reason)
