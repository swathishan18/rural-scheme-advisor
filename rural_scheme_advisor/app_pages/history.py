import streamlit as st

from database import (
    clear_conversations,
    delete_conversation,
    get_conversation,
    get_conversations,
)


if not st.session_state.get("user"):
    st.switch_page("app_pages/login.py")

user = st.session_state.user
st.title("Chat history", icon=":material/history:")

conversations = get_conversations(user["user_id"])

if conversations:
    if st.checkbox("Enable delete actions"):
        pass

    if st.button("Clear all history", icon=":material/delete_forever:", type="secondary"):
        st.session_state.confirm_clear_history = True
    if st.session_state.get("confirm_clear_history"):
        st.warning("This permanently deletes all of your conversations.")
        yes, no = st.columns(2)
        if yes.button("Yes, clear all", type="primary"):
            clear_conversations(user["user_id"])
            st.session_state.confirm_clear_history = False
            st.session_state.active_conversation_id = None
            st.session_state.chat_history = []
            st.rerun()
        if no.button("Cancel"):
            st.session_state.confirm_clear_history = False
            st.rerun()

    for conversation in conversations:
        with st.container(border=True):
            st.subheader(conversation["conversation_title"])
            st.caption(f"Updated: {conversation['updated_at']}")
            open_button, delete_button = st.columns(2)
            if open_button.button(
                "Open",
                key=f"open_history_{conversation['conversation_id']}",
                use_container_width=True,
            ):
                if get_conversation(conversation["conversation_id"], user["user_id"]):
                    st.session_state.active_conversation_id = conversation["conversation_id"]
                    st.switch_page("app_pages/chat.py")
            if delete_button.button(
                "Delete",
                key=f"delete_history_{conversation['conversation_id']}",
                use_container_width=True,
            ):
                st.session_state[f"confirm_delete_{conversation['conversation_id']}"] = True

            confirm_key = f"confirm_delete_{conversation['conversation_id']}"
            if st.session_state.get(confirm_key):
                st.warning("Delete this conversation?")
                yes, no = st.columns(2)
                if yes.button("Delete conversation", key=f"yes_{conversation['conversation_id']}"):
                    delete_conversation(conversation["conversation_id"], user["user_id"])
                    if st.session_state.get("active_conversation_id") == conversation["conversation_id"]:
                        st.session_state.active_conversation_id = None
                        st.session_state.chat_history = []
                    st.session_state[confirm_key] = False
                    st.rerun()
                if no.button("Cancel", key=f"no_{conversation['conversation_id']}"):
                    st.session_state[confirm_key] = False
                    st.rerun()
else:
    st.info("No previous conversations.")
