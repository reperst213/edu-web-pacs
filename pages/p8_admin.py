"""P8 관리 (FR-08·14, 계획서 9장). 담당: 팀원 1 · 12/8."""
import streamlit as st

from ui.common import require_actor

actor = require_actor()
st.title("관리")
st.info("준비 중 · 담당자 배정·재배정, 재오픈, 사용자 역할, 감사 로그 (팀원 1)")
