"""scripts/create_users.py 테스트. Firebase Auth·Firestore를 임시 객체로 바꿔 끼운다."""
import pytest

from scripts import create_users as cu


class TempAuth:
    class UserNotFoundError(Exception):
        pass

    def __init__(self):
        self.users: dict[str, dict] = {}   # email → {uid, password, display_name}
        self.deleted: list[str] = []

    def get_user_by_email(self, email):
        if email not in self.users:
            raise self.UserNotFoundError(email)
        return type("U", (), {"uid": self.users[email]["uid"]})

    def create_user(self, email, password, display_name):
        uid = f"uid-{len(self.users) + 1}"
        self.users[email] = {"uid": uid, "password": password, "display_name": display_name}
        return type("U", (), {"uid": uid})

    def delete_user(self, uid):
        self.deleted.append(uid)
        self.users = {e: u for e, u in self.users.items() if u["uid"] != uid}


class TempDb:
    def __init__(self, fail: bool = False):
        self.docs: dict[str, dict] = {}
        self.fail = fail

    def collection(self, name):
        assert name == "users"
        return self

    def document(self, uid):
        db = self

        class Ref:
            def get(self):
                return type("Snap", (), {"exists": uid in db.docs})

            def set(self, data, merge=False):
                if db.fail:
                    raise RuntimeError("Firestore 쓰기 실패")
                db.docs[uid] = {**db.docs.get(uid, {}), **data} if merge else dict(data)

        return Ref()


def test_accounts_match_plan():
    roles = [a.role for a in cu.ACCOUNTS]
    assert sorted(roles) == ["admin", "registrar", "reviewer", "reviewer"]
    assert len({a.local for a in cu.ACCOUNTS}) == 4


def test_creates_account_and_doc():
    fa, db = TempAuth(), TempDb()
    uid, created = cu.ensure_user(fa, db, "r@x.test", "검토자 1", "reviewer", "secret-pw")
    assert created
    assert fa.users["r@x.test"]["password"] == "secret-pw"
    doc = db.docs[uid]
    assert {k: doc[k] for k in ("email", "display_name", "role", "active")} == \
        {"email": "r@x.test", "display_name": "검토자 1", "role": "reviewer", "active": True}
    assert doc["created_at"].utcoffset().total_seconds() == 0


def test_rerun_is_safe_and_keeps_password_and_created_at():
    fa, db = TempAuth(), TempDb()
    uid, _ = cu.ensure_user(fa, db, "r@x.test", "검토자 1", "reviewer", "first-pw")
    first_created = db.docs[uid]["created_at"]

    uid2, created = cu.ensure_user(fa, db, "r@x.test", "검토자 1", "admin", "other-pw")
    assert (uid2, created) == (uid, False)
    assert fa.users["r@x.test"]["password"] == "first-pw"
    assert db.docs[uid]["role"] == "admin"
    assert db.docs[uid]["created_at"] == first_created


def test_existing_account_without_doc_gets_doc():
    fa, db = TempAuth(), TempDb()
    fa.create_user("a@x.test", "pw", "관리자 1")
    uid, created = cu.ensure_user(fa, db, "a@x.test", "관리자 1", "admin", "pw")
    assert not created
    assert db.docs[uid]["role"] == "admin" and "created_at" in db.docs[uid]


def test_doc_failure_rolls_back_new_account():
    fa, db = TempAuth(), TempDb(fail=True)
    with pytest.raises(RuntimeError):
        cu.ensure_user(fa, db, "r@x.test", "검토자 1", "reviewer", "pw")
    assert fa.users == {}
    assert fa.deleted == ["uid-1"]


def test_doc_failure_keeps_existing_account():
    fa, db = TempAuth(), TempDb(fail=True)
    fa.create_user("r@x.test", "pw", "검토자 1")
    with pytest.raises(RuntimeError):
        cu.ensure_user(fa, db, "r@x.test", "검토자 1", "reviewer", "pw")
    assert "r@x.test" in fa.users and fa.deleted == []


def test_dry_run_touches_nothing_and_prints_no_password(capsys, monkeypatch):
    monkeypatch.setattr(cu.getpass, "getpass", lambda *a: pytest.fail("비밀번호를 묻지 않아야 함"))
    assert cu.main(["--dry-run", "--domain", "example.test"]) == 0
    out = capsys.readouterr().out
    assert out.count("[dry-run]") == 4
    assert "reviewer2@example.test" in out


@pytest.mark.parametrize("inputs,msg", [
    (["short", "short"], "8자 이상"),
    (["long-enough-1", "long-enough-2"], "다릅니다"),
])
def test_read_password_rejects(monkeypatch, inputs, msg):
    it = iter(inputs)
    monkeypatch.setattr(cu.getpass, "getpass", lambda *a: next(it))
    with pytest.raises(SystemExit, match=msg):
        cu.read_password()
