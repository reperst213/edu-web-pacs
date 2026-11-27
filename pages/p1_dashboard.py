"""P1 대시보드 (계획서 9장). 담당: 팀원 1(틀) · 팀원 4(검토자 작업 목록, FR-10, 12/5)."""
import streamlit as st

from ui.common import require_actor

actor = require_actor()
st.title("대시보드")
st.info("준비 중 · 검토자: 처리할 업무 / 완료한 업무 탭 (팀원 4) · 등록 담당자·관리자 화면 (팀원 1)")
