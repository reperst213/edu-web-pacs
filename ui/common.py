"""공통 화면 부품 (계획서 17.5). 담당: 팀원 1.

모든 페이지는 맨 위에서 actor = require_actor() 를 호출한다.
서비스 함수 호출은 try/except로 감싸고, 예외는 show_error(e)로 보여준다.
"""
import logging

import streamlit as st

from services.errors import AppError
from services.types import ROLE_LABELS, Actor

BANNER = "교육용 모의 케이스 · 진단용 아님 · 데이터: ISIC 2020 Challenge Dataset (CC BY-NC)"
logger = logging.getLogger("dermapacs")


def show_banner() -> None:
    st.caption(f"**{BANNER}**")


def require_actor() -> Actor:
    """로그인한 사용자를 돌려준다. 없으면 안내 후 페이지 실행을 멈춘다."""
    actor = st.session_state.get("auth.actor")
    if actor is None:
        st.warning("로그인이 필요합니다.")
        st.stop()
    return actor


def show_actor(actor: Actor) -> None:
    st.sidebar.caption(f"{ROLE_LABELS[actor.role]} · {actor.email or actor.uid}")


def show_error(e: Exception) -> None:
    if isinstance(e, AppError):
        st.error(e.message)
    else:
        logger.exception("unexpected error")
        st.error("알 수 없는 오류가 발생했습니다. 다시 시도하고, 반복되면 단톡방에 알려 주세요.")
