"""P5 뷰어·처리 (FR-04~07, 계획서 7·9장). 담당: 팀원 3 · 12/5."""
import streamlit as st

from ui.common import require_actor

actor = require_actor()
st.title("뷰어 · 처리")
st.info("준비 중 · 원본/결과 2분할(Plotly, 축 공유), DICOM 태그, 알고리즘·ROI 패널, 처리 이력 (팀원 3)")
