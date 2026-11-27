"""DermaPACS-Edu 진입점 (계획서 9장, 17.4, 17.5). 담당: 팀원 1.

실행: uv run streamlit run app.py  →  http://localhost:8080
APP_MODE=local 이면 로그인 없이 사이드바에서 역할을 골라 개발한다.
"""
import os

import streamlit as st
from dotenv import load_dotenv

from services.types import ROLE_LABELS, ROLES, Actor
from ui.common import show_actor, show_banner

load_dotenv()
APP_MODE = os.getenv("APP_MODE", "local")
DEPLOY = os.getenv("DEPLOY", "0") == "1"

st.set_page_config(page_title="DermaPACS-Edu", layout="wide")

if DEPLOY and APP_MODE == "local":
    st.error("배포 환경(DEPLOY=1)에서는 로컬 개발 모드로 시작할 수 없습니다. .env의 APP_MODE를 확인하세요.")
    st.stop()


def local_actor() -> Actor:
    """로컬 개발 모드: 로그인만 건너뛴다. 권한 검사(require)는 그대로 거친다."""
    default = os.getenv("DEV_ROLE", "reviewer")
    role = st.sidebar.selectbox(
        "로컬 개발 모드 · 역할",
        ROLES,
        index=ROLES.index(default) if default in ROLES else 1,
        format_func=lambda r: ROLE_LABELS[r],
        key="auth.dev_role",
    )
    return Actor(uid=f"dev-{role}", role=role)


if APP_MODE == "local":
    st.session_state["auth.actor"] = local_actor()
else:
    # 팀원 1 · 12/1: services.auth.get_actor() 결과로 채운다.
    st.session_state.setdefault("auth.actor", None)

actor = st.session_state["auth.actor"]
show_banner()

login = st.Page("pages/p0_login.py", title="로그인")
dashboard = st.Page("pages/p1_dashboard.py", title="대시보드", default=True)
case_search = st.Page("pages/p2_case_search.py", title="케이스 검색")
case_register = st.Page("pages/p3_case_register.py", title="케이스 등록")
case_detail = st.Page("pages/p4_case_detail.py", title="케이스 상세")
viewer = st.Page("pages/p5_viewer.py", title="뷰어 · 처리")
similar = st.Page("pages/p6_similar_search.py", title="유사 병변 검색")
report = st.Page("pages/p7_report.py", title="리포트")
admin = st.Page("pages/p8_admin.py", title="관리")

if actor is None:
    nav = st.navigation([login])
else:
    show_actor(actor)
    work = [dashboard, case_search]
    if actor.role in ("registrar", "admin"):
        work.append(case_register)
    work += [case_detail, viewer]
    if actor.role in ("reviewer", "admin"):
        work.append(similar)
    work.append(report)
    menu = {"업무": work}
    if actor.role == "admin":
        menu["관리"] = [admin]
    nav = st.navigation(menu)

nav.run()
