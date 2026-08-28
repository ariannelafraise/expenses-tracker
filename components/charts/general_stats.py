import streamlit as st

from models import Transaction
from services.stats_service import calculate_general_stats


def draw(start_date, end_date):
    st.subheader("Overview")

    filters = [
        Transaction.date >= start_date,
        Transaction.date <= end_date,
    ]
    (
        total_transactions,
        debit_total,
        credit_total,
        average_transaction,
        largest_expense,
        largest_credit,
        cashback_total,
    ) = calculate_general_stats(filters)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Money Spent", f"${debit_total:,.2f}")
    with col2:
        st.metric("Money Received", f"${credit_total:,.2f}")
    with col3:
        st.metric("Total Transactions", total_transactions)
    with col4:
        st.metric("Average Expense", f"${average_transaction:,.2f}")

    col1, col2, col3, _ = st.columns(4)
    with col1:
        st.metric("Largest Expense", f"${largest_expense:,.2f}")
    with col2:
        st.metric("Largest Revenue", f"${largest_credit:,.2f}")
    with col3:
        st.metric("Total Cashback", f"${cashback_total:,.2f}")
