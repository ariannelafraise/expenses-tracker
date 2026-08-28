import streamlit as st

dashboard = st.Page(
    "pages/dashboard.py",
    title="Dashboard",
    icon=":material/dashboard:",
    default=True,
)

transactions = st.Page(
    "pages/transactions.py",
    title="Transactions",
    icon=":material/receipt_long:",
)

tags = st.Page(
    "pages/tags.py",
    title="Manage Tags",
    icon=":material/label:",
)

blacklist_keywords = st.Page(
    "pages/blacklist_keywords.py",
    title="Blacklist Keywords",
    icon=":material/block:",
)

add_transaction = st.Page(
    "pages/import_transactions.py",
    title="Import Transactions",
    icon=":material/add_circle:",
)

pg = st.navigation(
    [
        dashboard,
        transactions,
        tags,
        blacklist_keywords,
        add_transaction,
    ],
    position="top",
)

pg.run()
