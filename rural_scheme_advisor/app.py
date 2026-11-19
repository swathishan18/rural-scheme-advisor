import streamlit as st

from database import init_db


st.set_page_config(
    page_title="Rural Scheme Advisor",
    page_icon=":material/park:",
    layout="wide",
)
init_db()

st.session_state.setdefault("user", None)
st.session_state.setdefault("active_conversation_id", None)
st.session_state.setdefault("chat_history", [])
st.session_state.setdefault("chat_profile", {})


public_pages = {
    "": [
        st.Page(
            "app_pages/home.py",
            title="Home",
            icon=":material/home:",
            url_path="home",
            default=True,
            help="Overview of Rural Scheme Advisor and how it supports rural users.",
        ),
        st.Page(
            "app_pages/login.py",
            title="Login",
            icon=":material/login:",
            url_path="login",
            help="Sign in to access your dashboard and saved conversations.",
        ),
        st.Page(
            "app_pages/signup.py",
            title="Sign up",
            icon=":material/person_add:",
            url_path="signup",
            help="Create a secure account for personalised scheme assistance.",
        ),
    ]
}

private_pages = {
    "My account": [
        st.Page(
            "app_pages/dashboard.py",
            title="Dashboard",
            icon=":material/dashboard:",
            url_path="dashboard",
            default=True,
            help="View account activity, quick actions and recent scheme assistance.",
        ),
        st.Page(
            "app_pages/chat.py",
            title="Ask a question",
            icon=":material/chat:",
            url_path="chat",
            help="Ask scheme questions in Tamil or English using Agentic RAG.",
        ),
        st.Page(
            "app_pages/schemes.py",
            title="Explore schemes",
            icon=":material/account_balance:",
            url_path="schemes",
            help="Search and filter the government schemes available in project documents.",
        ),
        st.Page(
            "app_pages/eligibility.py",
            title="Eligibility checker",
            icon=":material/task_alt:",
            url_path="eligibility",
            help="Run a preliminary scheme eligibility screening.",
        ),
        st.Page(
            "app_pages/history.py",
            title="Chat history",
            icon=":material/history:",
            url_path="history",
            help="Open, continue or delete your saved conversations.",
        ),
        st.Page(
            "app_pages/profile.py",
            title="My profile",
            icon=":material/person:",
            url_path="profile",
            help="Update personal details, profile data and account password.",
        ),
    ]
}

if st.session_state.user:
    navigation = st.navigation(private_pages, position="sidebar")
    with st.sidebar:
        st.caption(f"Signed in as {st.session_state.user['full_name']}")
        if st.button("Logout", icon=":material/logout:", use_container_width=True):
            for key in (
                "user",
                "active_conversation_id",
                "chat_history",
                "chat_profile",
                "chat_last",
            ):
                st.session_state[key] = None if key == "user" or key == "active_conversation_id" else []
            st.session_state.chat_profile = {}
            st.rerun()
else:
    navigation = st.navigation(public_pages, position="top")

navigation.run()
