import streamlit as st

from auth import validate_password, verify_password, hash_password
from database import get_profile, get_user_by_id, save_profile, update_password, update_user


if not st.session_state.get("user"):
    st.switch_page("app_pages/login.py")

user_id = st.session_state.user["user_id"]
user = get_user_by_id(user_id)
profile_row = get_profile(user_id)

st.title("My profile", icon=":material/person:")
st.caption(f"Registered: {user['created_at']}")

st.subheader("Personal details")
with st.form("profile_details"):
    full_name = st.text_input("Full name", value=user["full_name"])
    email = st.text_input("Email address", value=user["email"], disabled=True)
    phone = st.text_input("Phone number", value=user["phone_number"] or "")
    state = st.text_input("State", value=user["state"] or "")
    saved = st.form_submit_button("Save details", type="primary")

if saved:
    if not full_name.strip():
        st.error("Full name cannot be empty.")
    else:
        update_user(user_id, full_name, phone, state)
        st.session_state.user = dict(get_user_by_id(user_id))
        st.success("Personal details updated.")

st.subheader("Eligibility profile")
profile = dict(profile_row) if profile_row else {}

def restore_selection(value):
    if value is None:
        return "Not selected"
    return "Yes" if value == 1 else "No"

with st.form("eligibility_profile"):
    age = st.number_input("Age", 0, 120, int(profile.get("age") or 0))
    gender = st.text_input("Gender", value=profile.get("gender") or "")
    occupation = st.text_input("Occupation", value=profile.get("occupation") or "")
    income = st.number_input(
        "Annual family income",
        0,
        100000000,
        int(profile.get("annual_income") or 0),
        step=1000,
    )
    profile_state = st.text_input("Eligibility state", value=profile.get("state") or user["state"] or "")
    owns_land = st.selectbox(
        "Owns cultivable land",
        ["Not selected", "Yes", "No"],
        index=["Not selected", "Yes", "No"].index(
            restore_selection(profile.get("owns_land"))
        ),
    )
    pucca = st.selectbox(
        "Has pucca house",
        ["Not selected", "Yes", "No"],
        index=["Not selected", "Yes", "No"].index(
            restore_selection(profile.get("has_pucca_house"))
        ),
    )
    girl_child = st.selectbox(
        "Has girl child under 10",
        ["Not selected", "Yes", "No"],
        index=["Not selected", "Yes", "No"].index(
            restore_selection(profile.get("has_girl_child_under_10"))
        ),
    )
    save_profile_data = st.form_submit_button("Save eligibility profile")

if save_profile_data:
    data = {
        "age": age or None,
        "gender": gender or None,
        "occupation": occupation or None,
        "annual_income": income,
        "state": profile_state or None,
        "owns_land": None if owns_land == "Not selected" else owns_land == "Yes",
        "has_pucca_house": None if pucca == "Not selected" else pucca == "Yes",
        "has_girl_child_under_10": None if girl_child == "Not selected" else girl_child == "Yes",
    }
    save_profile(user_id, data)
    st.session_state.chat_profile = data
    st.success("Eligibility profile saved.")

st.subheader("Change password")
with st.form("password_form"):
    current = st.text_input("Current password", type="password")
    new_password = st.text_input("New password", type="password")
    confirm_password = st.text_input("Confirm new password", type="password")
    changed = st.form_submit_button("Change password")

if changed:
    if not verify_password(current, user["password_hash"]):
        st.error("Current password is incorrect.")
    elif new_password != confirm_password:
        st.error("New passwords do not match.")
    else:
        valid, message = validate_password(new_password)
        if not valid:
            st.error(message)
        else:
            update_password(user_id, hash_password(new_password))
            st.success("Password changed successfully.")
