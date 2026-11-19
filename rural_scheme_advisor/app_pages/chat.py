import streamlit as st

from agent import answer
from config import NEXUS_API_KEY, NEXUS_BASE_URL
from database import (
    add_message,
    create_conversation,
    get_messages,
    get_profile,
    save_profile,
)
from rag import SchemeRetriever


@st.cache_resource(show_spinner="Loading scheme documents...")
def get_retriever():
    return SchemeRetriever()


if not st.session_state.get("user"):
    st.switch_page("app_pages/login.py")

if not NEXUS_API_KEY or not NEXUS_BASE_URL:
    st.error("Nexus API configuration is unavailable. It must be configured in the existing .env.")
    st.stop()

user = st.session_state.user
st.title("Ask a question", icon=":material/chat:")

language = st.segmented_control(
    "Reply language",
    ["Auto", "Tamil", "English"],
    selection_mode="single",
    default="Auto",
)
lang_map = {"Auto": "auto", "Tamil": "Tamil", "English": "English"}

saved_profile = get_profile(user["user_id"])
if saved_profile and not st.session_state.get("chat_profile"):
    st.session_state.chat_profile = {
        "age": saved_profile["age"],
        "gender": saved_profile["gender"],
        "occupation": saved_profile["occupation"],
        "annual_income": saved_profile["annual_income"],
        "owns_land": None if saved_profile["owns_land"] is None else bool(saved_profile["owns_land"]),
        "has_pucca_house": None if saved_profile["has_pucca_house"] is None else bool(saved_profile["has_pucca_house"]),
        "state": saved_profile["state"] or user["state"],
        "has_girl_child_under_10": (
            None if saved_profile["has_girl_child_under_10"] is None
            else bool(saved_profile["has_girl_child_under_10"])
        ),
    }

conversation_id = st.session_state.get("active_conversation_id")
if conversation_id:
    st.session_state.chat_history = [
        {"role": row["role"], "content": row["message_content"]}
        for row in get_messages(conversation_id, user["user_id"])
    ]

history = st.session_state.setdefault("chat_history", [])
profile = st.session_state.setdefault("chat_profile", {})

top = st.columns([4, 1])
with top[1]:
    if st.button("Clear chat", icon=":material/delete_sweep:", use_container_width=True):
        st.session_state.active_conversation_id = None
        st.session_state.chat_history = []
        st.session_state.chat_profile = {}
        st.session_state.chat_last = None
        st.rerun()

for message in history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input(
    "உங்கள் கேள்வியை கேளுங்கள் / Ask about a government scheme...",
    submit_mode="disable",
)

if prompt:
    if conversation_id is None:
        conversation_id = create_conversation(
            user["user_id"],
            prompt[:80].strip() or "Scheme assistance",
        )
        st.session_state.active_conversation_id = conversation_id

    add_message(conversation_id, user["user_id"], "user", prompt)
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=":material/psychology:"):
        with st.status(":shimmer[Searching scheme documents]", type="compact") as status:
            with st.status("Retrieving relevant documents", type="step"):
                retriever = get_retriever()
            with st.status("Checking preliminary eligibility", type="step"):
                reply, updated_profile, chunks, eligibility = answer(
                    prompt,
                    history,
                    profile,
                    retriever,
                    lang_map.get(language, "auto"),
                )
            status.update(label="Answer prepared", state="complete")
        st.markdown(reply)

    add_message(conversation_id, user["user_id"], "assistant", reply)
    history.extend([
        {"role": "user", "content": prompt},
        {"role": "assistant", "content": reply},
    ])
    st.session_state.chat_profile = updated_profile
    st.session_state.chat_last = (chunks, eligibility)
    save_profile(user["user_id"], updated_profile)
    st.rerun()

if st.session_state.get("chat_last"):
    chunks, eligibility = st.session_state.chat_last
    left, right = st.columns(2)
    with left:
        st.subheader("Preliminary eligibility")
        if eligibility:
            for name, reason, status in eligibility:
                st.write(f"**{name}** — {status}")
                st.caption(reason)
        else:
            st.caption("No eligibility result was identified.")
    with right:
        st.subheader("RAG sources")
        for hit in chunks:
            with st.expander(f"{hit['source']} (score {hit['score']:.2f})"):
                st.write(hit["text"])
