"""services.permissions.require() 테스트 (계획서 2장·18.2 매트릭스 전수).

동작 16개 × 역할 3개 × 본인 여부 2개 × 상태 5개를 모두 확인한다.
기대값은 계획서 표를 그대로 옮긴 SPEC에서 계산한다 (구현의 RULES와 따로 둔다).
"""
import itertools

import pytest

from services import audit, permissions
from services.errors import PermissionDenied
from services.permissions import ACTIONS, require
from services.types import ROLES, Actor, Status

# 계획서 18.2 표: action → {역할: (본인 조건, 필요한 상태)}
#   본인 조건: "" 없음 · "등록" 본인 등록 · "배정" 본인 배정
SPEC: dict[str, dict[str, tuple[str, str]]] = {
    "case.create":           {"registrar": ("", ""), "admin": ("", "")},
    "image.upload":          {"registrar": ("", ""), "admin": ("", "")},
    "case.update_intake":    {"registrar": ("등록", "RECEIVED"), "admin": ("", "")},
    "case.read":             {"registrar": ("등록", ""), "reviewer": ("배정", ""), "admin": ("", "")},
    "image.read":            {"registrar": ("등록", ""), "reviewer": ("배정", ""), "admin": ("", "")},
    "case.assign":           {"admin": ("", "")},
    "case.reopen":           {"admin": ("", "")},
    "user.manage":           {"admin": ("", "")},
    "audit.read":            {"admin": ("", "")},
    "process.run":           {"reviewer": ("배정", "IN_REVIEW")},
    "note.write":            {"reviewer": ("배정", "IN_REVIEW")},
    "search.run":            {"reviewer": ("배정", ""), "admin": ("", "")},
    "review.start":          {"reviewer": ("배정", "")},
    "review.complete":       {"reviewer": ("배정", "")},
    "review.request_rework": {"reviewer": ("배정", "")},
    "review.resubmit":       {"registrar": ("등록", "NEEDS_REWORK")},
}

ME = "u-me"
OTHER = "u-other"


def make_case(own: bool, status: Status) -> dict:
    uid = ME if own else OTHER
    return {"case_id": "MC-0001", "registered_by": uid, "assignee_uid": uid,
            "status": status.value, "version": 1}


def expected(action: str, role: str, own: bool, status: Status) -> bool:
    if role not in SPEC[action]:
        return False
    owner, need = SPEC[action][role]
    if owner and not own:
        return False
    if need and status.value != need:
        return False
    return True


@pytest.fixture
def audit_calls(monkeypatch):
    calls = []
    monkeypatch.setattr(audit, "log", lambda *a, **k: calls.append((a, k)))
    return calls


def test_spec_covers_all_actions():
    assert set(SPEC) == set(ACTIONS) == set(permissions.RULES)
    assert len(ACTIONS) == 16


MATRIX = list(itertools.product(ACTIONS, ROLES, [True, False], list(Status)))


@pytest.mark.parametrize("action,role,own,status", MATRIX,
                         ids=[f"{a}-{r}-{'own' if o else 'other'}-{s.value}"
                              for a, r, o, s in MATRIX])
def test_matrix(audit_calls, action, role, own, status):
    actor = Actor(uid=ME, role=role)
    case = make_case(own, status)
    if expected(action, role, own, status):
        require(actor, action, case)
        assert audit_calls == []
    else:
        with pytest.raises(PermissionDenied) as e:
            require(actor, action, case)
        assert e.value.message  # 화면에 보일 사유
        [(args, _)] = audit_calls
        assert args == (actor, action, "MC-0001", "deny", e.value.message)


def test_status_enum_value_in_case_also_works(audit_calls):
    case = {"case_id": "MC-0001", "assignee_uid": ME, "status": Status.IN_REVIEW}
    require(Actor(uid=ME, role="reviewer"), "process.run", case)


# ── 사유 문장 ──────────────────────────────────────────────

def test_reason_wrong_role(audit_calls):
    with pytest.raises(PermissionDenied, match="관리자만"):
        require(Actor(uid=ME, role="reviewer"), "case.assign")


def test_reason_not_registered_by_me(audit_calls):
    with pytest.raises(PermissionDenied, match="본인이 등록한"):
        require(Actor(uid=ME, role="registrar"), "case.read", make_case(False, Status.RECEIVED))


def test_reason_not_assigned_to_me(audit_calls):
    with pytest.raises(PermissionDenied, match="배정된 검토자만"):
        require(Actor(uid=ME, role="reviewer"), "review.start", make_case(False, Status.ASSIGNED))


def test_reason_wrong_status(audit_calls):
    with pytest.raises(PermissionDenied, match="'검토 중' 상태"):
        require(Actor(uid=ME, role="reviewer"), "note.write", make_case(True, Status.ASSIGNED))


# ── case 없이 부른 경우 ───────────────────────────────────

@pytest.mark.parametrize("action", ["case.create", "image.upload"])
def test_no_case_needed_for_create(audit_calls, action):
    require(Actor(uid=ME, role="registrar"), action)


@pytest.mark.parametrize("action", ["case.read", "case.update_intake", "search.run"])
def test_admin_needs_no_case(audit_calls, action):
    require(Actor(uid=ME, role="admin"), action)


@pytest.mark.parametrize("role,action", [
    ("registrar", "case.read"), ("reviewer", "case.read"),
    ("reviewer", "process.run"), ("registrar", "review.resubmit"),
])
def test_owner_rule_without_case_is_denied(audit_calls, role, action):
    with pytest.raises(PermissionDenied, match="케이스 정보가 없어"):
        require(Actor(uid=ME, role=role), action)
    [(args, _)] = audit_calls
    assert args[2] == ""  # target 없음


# ── 기타 ──────────────────────────────────────────────────

def test_unknown_action_is_code_error(audit_calls):
    with pytest.raises(ValueError):
        require(Actor(uid=ME, role="admin"), "case.delete")
    assert audit_calls == []


def test_audit_failure_still_denies(monkeypatch):
    def broken(*a, **k):
        raise RuntimeError("저장소 오류")
    monkeypatch.setattr(audit, "log", broken)
    with pytest.raises(PermissionDenied):
        require(Actor(uid=ME, role="reviewer"), "user.manage")


def test_deny_writes_real_audit_log():
    from tests.test_audit import TempRepo

    repo = TempRepo()
    audit.configure(repo)
    try:
        with pytest.raises(PermissionDenied):
            require(Actor(uid=ME, role="registrar"), "case.read", make_case(False, Status.DONE))
        [doc] = repo.query("audit_logs")
        assert (doc["actor_uid"], doc["action"], doc["target"], doc["result"]) == \
            (ME, "case.read", "MC-0001", "deny")
        assert doc["reason"]
    finally:
        audit.configure(None)
