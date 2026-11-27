"""로그인·세션 (FR-13). 담당: 팀원 1 · 기한 12/1.

방식(계획서 15장 R3): Firebase Auth REST API(signInWithPassword)로 로그인하고,
서버에서 firebase_admin.auth.verify_id_token()으로 ID 토큰을 검증한다.
만료(1시간) 전에 갱신 토큰으로 재발급한다. 역할은 Firestore users/{uid}.role에서 읽는다.
"""
from services.types import Actor, Session


def sign_in(email: str, password: str) -> Session:
    raise NotImplementedError("팀원 1 · 12/1")


def refresh(session: Session) -> Session:
    raise NotImplementedError("팀원 1 · 12/1")


def get_actor() -> Actor | None:
    """현재 로그인한 사용자. 로그인 안 됐으면 None (화면은 로그인 페이지로 보낸다)."""
    raise NotImplementedError("팀원 1 · 12/1")


def sign_out() -> None:
    raise NotImplementedError("팀원 1 · 12/1")
