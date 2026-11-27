"""P0 로그인 (FR-13, 계획서 9장). 담당: 팀원 1 · 12/1."""
import streamlit as st

st.title("로그인")
with st.form("login"):
    email = st.text_input("이메일")
    password = st.text_input("비밀번호", type="password")
    submitted = st.form_submit_button("로그인")
if submitted:
    st.info("준비 중 · 팀원 1이 12/1까지 services.auth.sign_in()으로 연결")
