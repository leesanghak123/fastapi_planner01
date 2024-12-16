import streamlit as st

# 로그인 시
def save_token(token):
    st.session_state['token'] = token

# API 요청 시
def get_token():
    return st.session_state.get('token')

# 로그아웃 시
def clear_token():
    st.session_state.pop('token', None)