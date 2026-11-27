"""P2 케이스 검색 (FR-03, 계획서 9장). 담당: 팀원 2 · 12/5."""
import streamlit as st

from ui.common import require_actor

actor = require_actor()
st.title("케이스 검색")
st.info("준비 중 · ID·상태·담당자·부위·등록일 필터 (팀원 2)")
