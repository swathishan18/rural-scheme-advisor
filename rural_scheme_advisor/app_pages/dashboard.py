import streamlit as st

from database import dashboard_stats

if not st.session_state.get("user"):
    st.switch_page("app_pages/login.py")

user = st.session_state.user
st.title(f"Welcome, {user['full_name']}", icon=":material/dashboard:")
conversations, questions, recent = dashboard_stats(user["user_id"])

c1, c2 = st.columns(2)
c1.metric("Questions asked", questions, border=True)
c2.metric("Conversations", conversations, border=True)

st.header("Quick actions")
actions = [
    ("Ask a question", "chat", "app_pages/chat.py"),
    ("Check eligibility", "task_alt", "app_pages/eligibility.py"),
    ("Explore schemes", "account_balance", "app_pages/schemes.py"),
    ("Chat history", "history", "app_pages/history.py"),
    ("My profile", "person", "app_pages/profile.py"),
]
cols = st.columns(3)
for index, (title, icon, target) in enumerate(actions):
    with cols[index % 3]:
        with st.container(border=True):
            st.subheader(title, icon=f":material/{icon}:")
            if st.button(title, key=f"dash_{index}", use_container_width=True):
                st.switch_page(target)

st.header("Recent conversations")
if recent:
    for title, updated_at in recent:
        st.caption(f"{title} - {updated_at}")
else:
    st.caption("No conversations yet.")
