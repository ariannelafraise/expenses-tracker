import streamlit as st

from services.tags_service import add_tag, get_all_tags, delete_tag

st.set_page_config(layout="centered")

st.title("Manage Tags")
st.caption("Organize transactions by assigning descriptive tags to them.")

# ============================================================
# Add tag
# ============================================================


def add_tag_callback():
    tag_name = st.session_state.tag_name_input.strip()

    if not tag_name:
        st.session_state.tag_error = "Tag name cannot be empty."
        return

    if not add_tag(tag_name):
        st.session_state.tag_error = "A tag with this name already exists."
        return

    st.session_state.tag_success = f"Tag '{tag_name}' created."
    st.session_state.tag_name_input = ""


with st.container(border=False):
    with st.form("add_tag"):
        st.text_input(
            "Name",
            placeholder="e.g. Groceries",
            key="tag_name_input",
            label_visibility="collapsed",
        )
        st.form_submit_button(
            "Add Tag",
            type="primary",
            use_container_width=True,
            on_click=add_tag_callback,
        )

if "tag_error" in st.session_state:
    st.error(st.session_state.pop("tag_error"))

if "tag_success" in st.session_state:
    st.success(st.session_state.pop("tag_success"))

st.divider()

# ============================================================
# Existing tags
# ============================================================

tags = get_all_tags()

if not tags:
    st.info("No tags created yet.")
else:
    st.caption(f"{len(tags)} tag{'s' if len(tags) != 1 else ''}")

    for tag in tags:
        with st.container(border=True):
            col_name, col_delete = st.columns([4, 1], vertical_alignment="center")

            with col_name:
                st.markdown(f"**{tag.name}**")

            with col_delete:
                if st.button(
                    "Delete",
                    key=f"delete_{tag.id}",
                    use_container_width=True,
                ):
                    delete_tag(tag.id)
                    st.rerun()
