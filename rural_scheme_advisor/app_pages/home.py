import streamlit as st

st.title("Rural Scheme Advisor", icon=":material/park:")
st.write(
    "Clear, practical help for Indian government schemes in Tamil and English."
)

col1, col2 = st.columns([2, 1])
with col1:
    st.header("Understand the right scheme")
    st.write(
        "Ask questions, check preliminary eligibility and explore official scheme "
        "documents with an Agentic RAG assistant."
    )
    if st.button("Get started", icon=":material/rocket_launch:", type="primary"):
        st.switch_page("app_pages/signup.py")
with col2:
    with st.container(border=True):
        st.metric("Languages", "Tamil + English")

st.header("How it helps")
cards = [
    ("Tamil and English", "Ask in the language you understand.", "translate"),
    ("Agentic RAG", "Answers are grounded in the project's scheme documents.", "smart_toy"),
    ("Eligibility guide", "Use a simple preliminary screening before official verification.", "task_alt"),
]
for title, text, icon in cards:
    with st.container(border=True):
        st.subheader(title, icon=f":material/{icon}:")
        st.write(text)

st.header("How it works")
st.write("1. Create an account  •  2. Ask or explore  •  3. Check eligibility  •  4. Verify officially")
login, signup = st.columns(2)
with login:
    if st.button("Login", use_container_width=True):
        st.switch_page("app_pages/login.py")
with signup:
    if st.button("Sign up", use_container_width=True, type="primary"):
        st.switch_page("app_pages/signup.py")
