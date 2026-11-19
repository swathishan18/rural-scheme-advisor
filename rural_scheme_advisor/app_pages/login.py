import streamlit as st

from auth import authenticate

st.title("Login", icon=":material/login:")

if st.session_state.get("user"):
    st.switch_page("app_pages/dashboard.py")

with st.form("login_form"):
    email = st.text_input("Email address")
    password = st.text_input("Password", type="password")
    remember = st.checkbox("Keep me logged in during this session")
    submitted = st.form_submit_button("Login", type="primary")

if submitted:
    user = authenticate(email, password)
    if not user:
        st.error("Invalid email or password.")
    else:
        st.session_state.user = user
        st.session_state.auth_remember = remember
        st.success("Login successful.")
        st.rerun()

st.caption("Do not have an account?")
if st.button("Create account"):
    st.switch_page("app_pages/signup.py")
