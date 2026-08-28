import streamlit as st

from services.transactions_service import import_from_json_file

st.set_page_config(layout="centered")

st.title("Import Transactions")

st.subheader("JSON Import")

uploaded_file = st.file_uploader(
    label="Upload a JSON exported from your bank.",
    accept_multiple_files=False,
    type=["json"],
    max_upload_size=50,
)

if uploaded_file is not None:
    if st.button(
        "Import",
        type="primary",
        width="stretch",
    ):
        imported, skipped, errors = import_from_json_file(uploaded_file)

        if errors:
            st.error(
                f"{errors} {"transactions" if errors > 1 else "transaction"} could not be parsed."
            )
            st.error(f"Transactions not imported due to errors.")
        else:
            st.success(f"Imported {imported} transactions.")

            if skipped:
                st.info(f"Skipped {skipped} rows.")
