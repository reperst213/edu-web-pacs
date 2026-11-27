"""P6 유사 병변 검색 (특화 기능, FR-15·16, 계획서 8장). 담당: 팀원 4 · 12/10."""
import streamlit as st

from ui.common import require_actor

actor = require_actor()
st.title("유사 병변 검색")
st.info("준비 중 · 질의 병변 + 비교 카드 K장, 참고 사례 선택 (팀원 4)")
