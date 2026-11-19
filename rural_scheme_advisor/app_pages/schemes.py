import os
import re
import streamlit as st
from pypdf import PdfReader

from config import DATA_DIR


def read_schemes():
    schemes = []
    for filename in sorted(os.listdir(DATA_DIR)):
        if not filename.lower().endswith((".txt", ".pdf")):
            continue
        path = os.path.join(DATA_DIR, filename)
        if filename.lower().endswith(".pdf"):
            reader = PdfReader(path)
            text = "\n".join(page.extract_text() or "" for page in reader.pages).strip()
        else:
            with open(path, "r", encoding="utf-8") as handle:
                text = handle.read().strip()
        name = text.split("\n", 1)[0].strip() if text else filename
        fields = {}
        for label in ("Benefits", "Eligibility", "Documents required", "How to apply"):
            match = re.search(
                rf"{label}:\s*(.*?)(?=(?:Benefits|Eligibility|Documents required|How to apply):|$)",
                text,
                flags=re.S,
            )
            fields[label] = match.group(1).strip() if match else ""
        category = "Housing" if "PMAY" in name.upper() else (
            "Health" if "Ayushman" in name else (
                "Employment" if "MGNREGA" in name else (
                    "Women and child" if "Sukanya" in name or "Magalir" in name else "Agriculture"
                )
            )
        )
        schemes.append({"name": name, "category": category, "filename": filename, **fields})
    return schemes


if not st.session_state.get("user"):
    st.switch_page("app_pages/login.py")

st.title("Explore government schemes", icon=":material/account_balance:")
schemes = read_schemes()

search = st.text_input("Search schemes", icon=":material/search:")
categories = ["All"] + sorted({item["category"] for item in schemes})
category = st.pills("Category", categories, selection_mode="single", default="All")

filtered = [
    item for item in schemes
    if (category in (None, "All") or item["category"] == category)
    and (not search or search.lower() in item["name"].lower())
]

if not filtered:
    st.info("No scheme matches your search.")
else:
    for item in filtered:
        with st.expander(item["name"], icon=":material/article:"):
            st.badge(item["category"], color="green")
            st.markdown(f"**Benefits**\n\n{item['Benefits'] or 'Not specified in the available document.'}")
            st.markdown(f"**Eligibility**\n\n{item['Eligibility'] or 'Not specified in the available document.'}")
            st.markdown(f"**Documents required**\n\n{item['Documents required'] or 'Not specified in the available document.'}")
            st.markdown(f"**How to apply**\n\n{item['How to apply'] or 'Not specified in the available document.'}")
            st.caption(
                f"Source: {item['filename']}. "
                "This information is preliminary; verify current rules and benefits on an official government source."
            )
