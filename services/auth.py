"""로그인·세션 (FR-13). 담당: 팀원 1 · 기한 12/1.

방식(계획서 15장 R3): Firebase Auth REST API(signInWithPassword)로 로그인하고,
서버에서 firebase_admin.auth.verify_id_token()으로 ID 토큰을 검증한다.
만료(1시간) 전에 갱신 토큰으로 재발급한다. 역할은 Firestore users/{uid}.role에서 읽는다.

- 세션은 st.session_state["auth.session"]에 둔다 (접두어 auth.).
- users 문서는 repositories.base.Repository로 읽는다. 앱 시작 시 configure(repo).
- Actor는 검증된 토큰의 uid + DB의 role로만 만든다.
"""
import logging
import os
import time
from typing import Any, MutableMapping

import requests

from repositories.base import Repository
from services.errors import AppError, PermissionDenied, ValidationError
from services.types import ROLES, Actor, Session

logger = logging.getLogger(__name__)

SIGN_IN_URL = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
REFRESH_URL = "https://securetoken.googleapis.com/v1/token"
TIMEOUT = 10            # 초
REFRESH_MARGIN = 300    # 만료 5분 전이면 갱신
SESSION_KEY = "auth.session"

# Firebase 오류 코드 → 화면 문장
_ERRORS: dict[str, tuple[type[AppError], str]] = {
    "INVALID_LOGIN_CREDENTIALS": (ValidationError, "이메일 또는 비밀번호가 올바르지 않습니다."),
    "EMAIL_NOT_FOUND": (ValidationError, "이메일 또는 비밀번호가 올바르지 않습니다."),
    "INVALID_PASSWORD": (ValidationError, "이메일 또는 비밀번호가 올바르지 않습니다."),
    "INVALID_EMAIL": (ValidationError, "이메일 형식이 올바르지 않습니다."),
    "MISSING_PASSWORD": (ValidationError, "비밀번호를 입력하세요."),
    "USER_DISABLED": (PermissionDenied, "사용이 중지된 계정입니다. 관리자에게 문의하세요."),
    "TOO_MANY_ATTEMPTS_TRY_LATER": (PermissionDenied, "로그인 시도가 너무 많습니다. 잠시 후 다시 시도하세요."),
    "TOKEN_EXPIRED": (PermissionDenied, "로그인이 만료되었습니다. 다시 로그인하세요."),
    "INVALID_REFRESH_TOKEN": (PermissionDenied, "로그인이 만료되었습니다. 다시 로그인하세요."),
    "USER_NOT_FOUND": (PermissionDenied, "계정을 찾을 수 없습니다. 관리자에게 문의하세요."),
}

_repo: Repository | None = None


def configure(repo: Repository | None) -> None:
    """users 문서를 읽을 저장소를 정한다. None이면 설정을 지운다 (테스트용)."""
    global _repo
    _repo = repo


# ── 바꿔 끼울 수 있는 부분 (테스트에서 대체) ─────────────────

def _state() -> MutableMapping[str, Any]:
    import streamlit as st
    return st.session_state


def _verify(id_token: str) -> str:
    """ID 토큰을 Admin SDK로 검증하고 uid를 돌려준다."""
    import firebase_admin
    from firebase_admin import auth as fb_auth

    if not firebase_admin._apps:
        firebase_admin.initialize_app()  # GOOGLE_APPLICATION_CREDENTIALS 사용
    return fb_auth.verify_id_token(id_token)["uid"]


def _post(url: str, **kwargs) -> dict:
    api_key = os.getenv("FIREBASE_WEB_API_KEY")
    if not api_key:
        raise RuntimeError("FIREBASE_WEB_API_KEY가 설정되지 않았습니다 (.env 확인).")
    try:
        resp = requests.post(url, params={"key": api_key}, timeout=TIMEOUT, **kwargs)
    except requests.RequestException as e:
        logger.warning("Firebase Auth 연결 실패: %s", e)
        raise AppError("로그인 서버에 연결할 수 없습니다. 잠시 후 다시 시도하세요.") from None
    body = resp.json() if resp.content else {}
    if resp.status_code != 200:
        raise _to_error(body)
    return body


def _to_error(body: dict) -> AppError:
    raw = str(body.get("error", {}).get("message", ""))
    code = raw.split(":")[0].strip()  # 예: "TOO_MANY_ATTEMPTS_TRY_LATER : ..."
    cls, msg = _ERRORS.get(code, (AppError, "로그인 중 오류가 발생했습니다. 다시 시도하세요."))
    if code not in _ERRORS:
        logger.warning("알 수 없는 Firebase Auth 오류: %s", raw)
    return cls(msg)


# ── 공개 함수 ─────────────────────────────────────────────

def sign_in(email: str, password: str) -> Session:
    email = email.strip()
    if not email or not password:
        raise ValidationError("이메일과 비밀번호를 입력하세요.")
    body = _post(SIGN_IN_URL, json={
        "email": email, "password": password, "returnSecureToken": True})
    session = Session(
        uid=body["localId"],
        email=body.get("email", email),
        id_token=body["idToken"],
        refresh_token=body["refreshToken"],
        expires_at=time.time() + int(body["expiresIn"]),
    )
    _state()[SESSION_KEY] = session
    return session


def refresh(session: Session) -> Session:
    body = _post(REFRESH_URL, data={
        "grant_type": "refresh_token", "refresh_token": session.refresh_token})
    return Session(
        uid=body["user_id"],
        email=session.email,
        id_token=body["id_token"],
        refresh_token=body["refresh_token"],
        expires_at=time.time() + int(body["expires_in"]),
    )


def get_actor() -> Actor | None:
    """현재 로그인한 사용자. 로그인 안 됐으면 None (화면은 로그인 페이지로 보낸다).

    갱신 실패·토큰 검증 실패면 세션을 지우고 None.
    계정이 비활성이거나 역할이 없으면 세션을 지우고 PermissionDenied.
    """
    state = _state()
    session: Session | None = state.get(SESSION_KEY)
    if session is None:
        return None
    try:
        if session.expires_at - time.time() < REFRESH_MARGIN:
            session = refresh(session)
            state[SESSION_KEY] = session
        uid = _verify(session.id_token)
    except AppError:
        sign_out()
        return None
    except Exception:
        logger.exception("ID 토큰 검증 실패")
        sign_out()
        return None

    if _repo is None:
        raise RuntimeError("auth.configure(repo)를 먼저 호출해야 합니다.")
    user = _repo.get("users", uid)
    if not user or not user.get("active", False):
        sign_out()
        raise PermissionDenied("사용할 수 없는 계정입니다. 관리자에게 문의하세요.")
    role = user.get("role")
    if role not in ROLES:
        sign_out()
        raise PermissionDenied("역할이 지정되지 않은 계정입니다. 관리자에게 문의하세요.")
    return Actor(uid=uid, role=role, email=user.get("email", session.email))


def sign_out() -> None:
    state = _state()
    for key in [k for k in state.keys() if str(k).startswith("auth.")]:
        del state[key]
