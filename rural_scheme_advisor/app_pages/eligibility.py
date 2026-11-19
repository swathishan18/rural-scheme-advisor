import streamlit as st

from eligibility import check_eligibility
from database import get_profile, save_profile


if not st.session_state.get("user"):
    st.switch_page("app_pages/login.py")

user = st.session_state.user
saved = get_profile(user["user_id"])
saved_profile = dict(saved) if saved else {}

gender_options = ["", "Female", "Male", "Other"]
saved_gender = str(saved_profile.get("gender") or "").strip().title()
gender_index = gender_options.index(saved_gender) if saved_gender in gender_options else 0

def _restore_selection(value, yes_label="Yes", no_label="No"):
    if value is None:
        return "Not selected"
    return yes_label if value == 1 else no_label

st.title("Eligibility checker", icon=":material/task_alt:")
st.caption("Preliminary screening only - official eligibility is decided by the responsible authority.")

with st.form("eligibility_form"):
    age = st.number_input("Age", min_value=0, max_value=120, value=int(saved_profile.get("age") or 0))
    gender = st.selectbox(
        "Gender",
        gender_options,
        index=gender_index,
    )
    occupation = st.text_input("Occupation", value=saved_profile.get("occupation") or "")
    income = st.number_input(
        "Annual family income (INR)",
        min_value=0,
        max_value=100000000,
        value=int(saved_profile.get("annual_income") or 0),
        step=1000,
    )
    state = st.text_input("State", value=saved_profile.get("state") or user["state"] or "")
    owns_land = st.selectbox(
        "Do you own cultivable land?",
        ["Not selected", "Yes", "No"],
        index=["Not selected", "Yes", "No"].index(
            _restore_selection(saved_profile.get("owns_land"))
        ),
    )
    pucca = st.selectbox(
        "Do you live in a pucca house?",
        ["Not selected", "Yes", "No"],
        index=["Not selected", "Yes", "No"].index(
            _restore_selection(saved_profile.get("has_pucca_house"))
        ),
    )
    girl_child = st.selectbox(
        "Do you have a girl child under 10?",
        ["Not selected", "Yes", "No"],
        index=["Not selected", "Yes", "No"].index(
            _restore_selection(saved_profile.get("has_girl_child_under_10"))
        ),
    )
    consent = st.checkbox("Save this profile for personalised scheme assistance")
    submitted = st.form_submit_button("Check eligibility", type="primary")

if submitted:
    if age < 1:
        st.error("Enter a valid age.")
    else:
        profile = {
            "age": age,
            "gender": gender or None,
            "occupation": occupation or None,
            "annual_income": income,
            "state": state or None,
            "owns_land": None if owns_land == "Not selected" else owns_land == "Yes",
            "has_pucca_house": None if pucca == "Not selected" else pucca == "Yes",
            "has_girl_child_under_10": None if girl_child == "Not selected" else girl_child == "Yes",
        }
        if consent:
            save_profile(user["user_id"], profile)
            st.success("Eligibility profile saved.")
        results = check_eligibility(profile)
        if not results:
            st.info("No likely scheme was identified from the details provided.")
        for name, reason, status in results:
            with st.container(border=True):
                st.subheader(name)
                st.badge(status, color="green" if status == "Likely" else "orange")
                st.write(reason)
                st.caption("Additional documents or official verification may be required.")
