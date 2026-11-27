"""P4 케이스 상세 (계획서 9장). 담당: 팀원 4 · 12/5 (메모 패널은 팀원 2의 ui/notes_panel.py)."""
import streamlit as st

from ui.common import require_actor

actor = require_actor()
st.title("케이스 상세")
st.info("준비 중 · 정보, 영상 썸네일, 상태·담당자, 상태 변경 버튼, 이벤트 이력 (팀원 4) · 메모 (팀원 2)")
