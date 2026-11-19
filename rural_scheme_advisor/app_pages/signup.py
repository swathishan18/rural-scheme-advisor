import sqlite3
import streamlit as st

from auth import hash_password, validate_email, validate_password
from database import create_user, get_user_by_email

st.title("Create account", icon=":material/person_add:")

with st.form("signup_form"):
    full_name = st.text_input("Full name")
    email = st.text_input("Email address")
    phone = st.text_input("Phone number (optional)")
    state = st.text_input("State")
    password = st.text_input("Password", type="password")
    confirm = st.text_input("Confirm password", type="password")
    submitted = st.form_submit_button("Register", type="primary")

if submitted:
    if not full_name.strip():
        st.error("Enter your full name.")
    elif not validate_email(email):
        st.error("Enter a valid email address.")
    elif password != confirm:
        st.error("Passwords do not match.")
    else:
        valid, message = validate_password(password)
        if not valid:
            st.error(message)
        elif get_user_by_email(email):
            st.error("An account with this email already exists.")
        else:
            try:
                create_user(full_name, email, hash_password(password), phone, state)
                st.success("Registration successful. Please login.")
            except sqlite3.IntegrityError:
                st.error("An account with this email already exists.")

if st.button("Already have an account? Login"):
    st.switch_page("app_pages/login.py")
