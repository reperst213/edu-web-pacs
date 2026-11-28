"""services.auth 테스트. 실제 Firebase를 부르지 않는다.

HTTP(requests.post), 토큰 검증(_verify), 세션 상태(_state), 저장소를 임시로 바꿔 끼운다.
"""
import time

import pytest
import requests

from repositories.base import Repository
from services import auth
from services.errors import AppError, PermissionDenied, ValidationError
from services.types import Actor, Session


class TempUsers(Repository):
    def __init__(self, users: dict[str, dict]):
        self.users = users

    def get(self, col, id):
        assert col == "users"
        return self.users.get(id)

    def create(self, col, id, data):
        raise NotImplementedError

    def update(self, col, id, data):
        raise NotImplementedError

    def query(self, col, where=None, order_by=None, limit=None, start_after=None):
        raise NotImplementedError

    def run_transaction(self, fn):
        return fn(self)


class Resp:
    def __init__(self, status: int, body: dict):
        self.status_code = status
        self._body = body
        self.content = b"x"

    def json(self):
        return self._body


SIGN_IN_OK = {"localId": "u1", "email": "a@test.kr", "idToken": "id-1",
              "refreshToken": "rt-1", "expiresIn": "3600"}
REFRESH_OK = {"user_id": "u1", "id_token": "id-2", "refresh_token": "rt-2", "expires_in": "3600"}


def fb_error(code: str) -> Resp:
    return Resp(400, {"error": {"code": 400, "message": code}})


@pytest.fixture
def env(monkeypatch):
    state: dict = {}
    calls: list[tuple[str, dict]] = []
    responses: list = []

    def post(url, **kwargs):
        calls.append((url, kwargs))
        r = responses.pop(0)
        if isinstance(r, Exception):
            raise r
        return r

    monkeypatch.setenv("FIREBASE_WEB_API_KEY", "test-key")
    monkeypatch.setattr(auth, "_state", lambda: state)
    monkeypatch.setattr(auth, "_verify", lambda token: {"id-1": "u1", "id-2": "u1"}[token])
    monkeypatch.setattr(requests, "post", post)
    users = TempUsers({"u1": {"email": "a@test.kr", "role": "reviewer", "active": True}})
    auth.configure(users)
    yield type("Env", (), {"state": state, "calls": calls, "responses": responses, "users": users})
    auth.configure(None)


# ── sign_in ──────────────────────────────────────────────

def test_sign_in_returns_and_stores_session(env):
    env.responses.append(Resp(200, SIGN_IN_OK))
    before = time.time()
    s = auth.sign_in(" a@test.kr ", "pw")
    assert (s.uid, s.email, s.id_token, s.refresh_token) == ("u1", "a@test.kr", "id-1", "rt-1")
    assert before + 3600 <= s.expires_at <= time.time() + 3600
    assert env.state[auth.SESSION_KEY] is s

    url, kw = env.calls[0]
    assert url == auth.SIGN_IN_URL
    assert kw["params"] == {"key": "test-key"}
    assert kw["json"] == {"email": "a@test.kr", "password": "pw", "returnSecureToken": True}
    assert kw["timeout"] == auth.TIMEOUT


@pytest.mark.parametrize("email,pw", [("", "pw"), ("  ", "pw"), ("a@test.kr", "")])
def test_sign_in_requires_input(env, email, pw):
    with pytest.raises(ValidationError):
        auth.sign_in(email, pw)
    assert env.calls == []


@pytest.mark.parametrize("code,cls,text", [
    ("INVALID_LOGIN_CREDENTIALS", ValidationError, "올바르지 않습니다"),
    ("EMAIL_NOT_FOUND", ValidationError, "올바르지 않습니다"),
    ("INVALID_PASSWORD", ValidationError, "올바르지 않습니다"),
    ("USER_DISABLED", PermissionDenied, "사용이 중지된"),
    ("TOO_MANY_ATTEMPTS_TRY_LATER : Access disabled", PermissionDenied, "너무 많습니다"),
    ("SOMETHING_NEW", AppError, "로그인 중 오류"),
])
def test_sign_in_firebase_errors(env, code, cls, text):
    env.responses.append(fb_error(code))
    with pytest.raises(cls, match=text) as e:
        auth.sign_in("a@test.kr", "pw")
    assert type(e.value) is cls
    assert auth.SESSION_KEY not in env.state


def test_wrong_email_and_wrong_password_look_the_same(env):
    env.responses += [fb_error("EMAIL_NOT_FOUND"), fb_error("INVALID_PASSWORD")]
    msgs = []
    for _ in range(2):
        with pytest.raises(ValidationError) as e:
            auth.sign_in("a@test.kr", "pw")
        msgs.append(e.value.message)
    assert msgs[0] == msgs[1]


def test_sign_in_network_error(env):
    env.responses.append(requests.ConnectionError("down"))
    with pytest.raises(AppError, match="연결할 수 없습니다"):
        auth.sign_in("a@test.kr", "pw")


def test_missing_api_key(env, monkeypatch):
    monkeypatch.delenv("FIREBASE_WEB_API_KEY")
    with pytest.raises(RuntimeError):
        auth.sign_in("a@test.kr", "pw")


# ── refresh ──────────────────────────────────────────────

def test_refresh(env):
    env.responses.append(Resp(200, REFRESH_OK))
    old = Session("u1", "a@test.kr", "id-1", "rt-1", time.time())
    new = auth.refresh(old)
    assert (new.uid, new.email, new.id_token, new.refresh_token) == ("u1", "a@test.kr", "id-2", "rt-2")
    url, kw = env.calls[0]
    assert url == auth.REFRESH_URL
    assert kw["data"] == {"grant_type": "refresh_token", "refresh_token": "rt-1"}


def test_refresh_expired(env):
    env.responses.append(fb_error("TOKEN_EXPIRED"))
    with pytest.raises(PermissionDenied, match="다시 로그인"):
        auth.refresh(Session("u1", "a@test.kr", "id-1", "rt-1", time.time()))


# ── get_actor ────────────────────────────────────────────

def login(env, expires_in: float = 3600):
    env.state[auth.SESSION_KEY] = Session("u1", "a@test.kr", "id-1", "rt-1", time.time() + expires_in)


def test_get_actor_none_when_logged_out(env):
    assert auth.get_actor() is None


def test_get_actor_uses_db_role(env):
    login(env)
    assert auth.get_actor() == Actor(uid="u1", role="reviewer", email="a@test.kr")
    assert env.calls == []  # 만료 전이라 갱신 안 함


def test_get_actor_reads_role_every_time(env):
    login(env)
    assert auth.get_actor().role == "reviewer"
    env.users.users["u1"]["role"] = "admin"
    assert auth.get_actor().role == "admin"


def test_get_actor_uid_comes_from_verified_token(env, monkeypatch):
    env.users.users["u2"] = {"email": "b@test.kr", "role": "admin", "active": True}
    env.state[auth.SESSION_KEY] = Session("u2", "b@test.kr", "id-1", "rt-1", time.time() + 3600)
    assert auth.get_actor().uid == "u1"  # 세션에 적힌 uid가 아니라 토큰의 uid


def test_get_actor_refreshes_near_expiry(env):
    login(env, expires_in=60)
    env.responses.append(Resp(200, REFRESH_OK))
    assert auth.get_actor().uid == "u1"
    assert env.state[auth.SESSION_KEY].id_token == "id-2"


def test_get_actor_signs_out_when_refresh_fails(env):
    login(env, expires_in=60)
    env.state["auth.other"] = 1
    env.responses.append(fb_error("TOKEN_EXPIRED"))
    assert auth.get_actor() is None
    assert not any(k.startswith("auth.") for k in env.state)


def test_get_actor_signs_out_when_verify_fails(env, monkeypatch):
    def bad(token):
        raise ValueError("invalid signature")
    monkeypatch.setattr(auth, "_verify", bad)
    login(env)
    assert auth.get_actor() is None
    assert auth.SESSION_KEY not in env.state


@pytest.mark.parametrize("user", [
    None,
    {"email": "a@test.kr", "role": "reviewer", "active": False},
    {"email": "a@test.kr", "role": "reviewer"},
])
def test_get_actor_rejects_unusable_account(env, user):
    if user is None:
        del env.users.users["u1"]
    else:
        env.users.users["u1"] = user
    login(env)
    with pytest.raises(PermissionDenied, match="사용할 수 없는 계정"):
        auth.get_actor()
    assert auth.SESSION_KEY not in env.state


@pytest.mark.parametrize("role", [None, "", "superuser"])
def test_get_actor_rejects_bad_role(env, role):
    env.users.users["u1"]["role"] = role
    login(env)
    with pytest.raises(PermissionDenied, match="역할이 지정되지"):
        auth.get_actor()


def test_get_actor_requires_configure(env):
    auth.configure(None)
    login(env)
    with pytest.raises(RuntimeError):
        auth.get_actor()


# ── sign_out ─────────────────────────────────────────────

def test_sign_out_removes_only_auth_keys(env):
    login(env)
    env.state["auth.actor"] = "x"
    env.state["case.selected"] = "MC-0001"
    auth.sign_out()
    assert env.state == {"case.selected": "MC-0001"}
