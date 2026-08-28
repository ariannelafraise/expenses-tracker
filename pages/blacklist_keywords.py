import streamlit as st

from services.blacklist_service import (
    add_blacklist_keyword,
    get_all_blacklist_keywords,
    delete_blacklist_keyword,
)

st.set_page_config(layout="centered")

st.title("Blacklist Keywords")
st.caption("Transactions matching these keywords will be skipped during JSON imports.")

# ============================================================
# Add blacklist keyword
# ============================================================


def add_keyword_callback():
    keyword = st.session_state.blacklist_keyword_input.strip()
    strict = st.session_state.blacklist_keyword_strict

    if not keyword:
        st.session_state.blacklist_keyword_error = "Keyword cannot be empty."
        return

    if not add_blacklist_keyword(keyword, strict):
        st.session_state.blacklist_keyword_error = "This keyword already exists."
        return

    st.session_state.blacklist_keyword_success = (
        f"Blacklist keyword '{keyword}' created."
    )
    st.session_state.blacklist_keyword_input = ""


with st.container(border=False):
    with st.form("add_blacklist_keyword"):
        st.text_input(
            "Keyword",
            placeholder="e.g. Credit card",
            key="blacklist_keyword_input",
            label_visibility="collapsed",
        )
        st.checkbox(
            "Strict match",
            help="The entire transaction description must match the keyword.",
            key="blacklist_keyword_strict",
        )
        st.form_submit_button(
            "Add Keyword",
            type="primary",
            width="stretch",
            on_click=add_keyword_callback,
        )

if "blacklist_keyword_error" in st.session_state:
    st.error(st.session_state.pop("blacklist_keyword_error"))

if "blacklist_keyword_success" in st.session_state:
    st.success(st.session_state.pop("blacklist_keyword_success"))

st.divider()

# ============================================================
# Existing blacklist keywords
# ============================================================

keywords = get_all_blacklist_keywords()

if not keywords:
    st.info("No blacklist keywords created yet.")
else:
    st.caption(f"{len(keywords)} keyword{'s' if len(keywords) != 1 else ''}")

    for keyword in keywords:
        with st.container(border=True):
            col_name, col_type, col_delete = st.columns(
                [3, 2, 1],
                vertical_alignment="center",
            )

            with col_name:
                st.markdown(f"**{keyword.keyword}**")

            with col_type:
                if keyword.strict:
                    st.caption("Strict match")
                else:
                    st.caption("Keyword match")

            with col_delete:
                if st.button(
                    "Delete",
                    key=f"delete_{keyword.id}",
                    use_container_width=True,
                ):
                    delete_blacklist_keyword(keyword.id)
                    st.rerun()
