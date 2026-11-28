"""services.audit 테스트. 간단한 가짜 저장소로 기록 내용을 확인한다."""
from datetime import datetime, timedelta, timezone

import pytest

from repositories.base import Repository
from services import audit
from services.types import Actor


class FakeRepo(Repository):
    def __init__(self):
        self.docs: dict[str, dict[str, dict]] = {}

    def get(self, col, id):
        return self.docs.get(col, {}).get(id)

    def create(self, col, id, data):
        bucket = self.docs.setdefault(col, {})
        if id in bucket:
            raise KeyError(id)
        bucket[id] = dict(data)

    def update(self, col, id, data):
        self.docs[col][id].update(data)

    def query(self, col, where=None, order_by=None, limit=None, start_after=None):
        return list(self.docs.get(col, {}).values())

    def run_transaction(self, fn):
        return fn(self)


ADMIN = Actor(uid="u-admin", role="admin")


@pytest.fixture
def repo():
    r = FakeRepo()
    audit.configure(r)
    yield r
    audit.configure(None)


def test_log_writes_all_fields(repo):
    before = datetime.now(timezone.utc)
    audit.log(ADMIN, "case.assign", "MC-0001", "allow")
    after = datetime.now(timezone.utc)

    [doc] = repo.query("audit_logs")
    assert doc["actor_uid"] == "u-admin"
    assert doc["action"] == "case.assign"
    assert doc["target"] == "MC-0001"
    assert doc["result"] == "allow"
    assert doc["reason"] == ""
    assert before <= doc["at"] <= after
    assert doc["at"].utcoffset() == timedelta(0)


def test_log_keeps_reason(repo):
    audit.log(ADMIN, "case.read", "MC-0002", "deny", reason="배정된 검토자만 볼 수 있습니다.")
    [doc] = repo.query("audit_logs")
    assert doc["reason"] == "배정된 검토자만 볼 수 있습니다."


def test_each_log_is_a_new_document(repo):
    for _ in range(3):
        audit.log(ADMIN, "case.read", "MC-0001", "allow")
    assert len(repo.query("audit_logs")) == 3


@pytest.mark.parametrize("result", ["allow", "deny", "error"])
def test_accepts_known_results(repo, result):
    audit.log(ADMIN, "case.read", "MC-0001", result)
    assert repo.query("audit_logs")[0]["result"] == result


@pytest.mark.parametrize("result", ["ok", "DENY", ""])
def test_rejects_unknown_result(repo, result):
    with pytest.raises(ValueError):
        audit.log(ADMIN, "case.read", "MC-0001", result)
    assert repo.query("audit_logs") == []


def test_requires_configure():
    audit.configure(None)
    with pytest.raises(RuntimeError):
        audit.log(ADMIN, "case.read", "MC-0001", "allow")
