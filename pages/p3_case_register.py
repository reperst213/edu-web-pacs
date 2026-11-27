"""P3 케이스 등록 (FR-01·02, 계획서 9장). 담당: 팀원 2 · 12/5."""
import streamlit as st

from ui.common import require_actor

actor = require_actor()
st.title("케이스 등록")
st.info("준비 중 · 검사 정보 입력, 여러 영상 업로드, 파일별 성공·실패 표 (팀원 2)")
