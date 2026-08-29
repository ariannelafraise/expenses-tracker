import streamlit as st

from services.transactions_service import (
    get_all_transactions,
    get_min_max_dates,
    update_transaction_tags,
)
from services.tags_service import get_all_tags_names
from services.stats_service import calculate_general_stats
from models import Transaction, Tag, TransactionDirection

PAGE_SIZE = 50

# ============================================================
# Initialize Session State
# ============================================================

if "expense_page" not in st.session_state:
    st.session_state.expense_page = 1
if "recently_tagged_transactions" not in st.session_state:
    st.session_state.recently_tagged_transactions = set()

# ============================================================
# Tag Update Callback
# ============================================================


def update_transaction_tags_callback(transaction_id, widget_key):
    selected_tag_names = st.session_state[widget_key]
    update_transaction_tags(transaction_id, selected_tag_names)

    # Keep a newly tagged transaction visible while
    # "Untagged only" is enabled.
    if selected_tag_names:
        st.session_state.recently_tagged_transactions.add(transaction_id)
    else:
        st.session_state.recently_tagged_transactions.discard(transaction_id)


# ============================================================
# Initialize Page
# ============================================================

st.set_page_config(layout="wide")

st.title("Transactions")

min_date, max_date = get_min_max_dates()

if min_date is None:
    st.info("No transactions yet. " "Import transactions to get started.")
    st.stop()

tag_names = get_all_tags_names()

# ============================================================
# Stats
# ============================================================

# Reserves the position above the filters. Stats will be calculated and added after filtering occurs.
stats_placeholder = st.empty()

# ============================================================
# Filtering controls
# ============================================================

st.subheader("Filter")

with st.container(border=True):
    filter_col1, filter_col2, filter_col3 = st.columns([1, 1, 2])

    with filter_col1:
        start_date = st.date_input(
            "From",
            value=min_date,
            min_value=min_date,
            max_value=max_date,
        )

    with filter_col2:
        end_date = st.date_input(
            "To",
            value=max_date,
            min_value=min_date,
            max_value=max_date,
        )

    with filter_col3:
        selected_tags = st.multiselect("Tags", placeholder="Tags", options=tag_names)

    show_untagged = st.checkbox("Untagged only")

# ============================================================
# Reset pagination when filters change
# ============================================================

filter_state = (
    start_date,
    end_date,
    tuple(selected_tags),
    show_untagged,
)

if "previous_filter_state" not in st.session_state:
    st.session_state.previous_filter_state = filter_state
elif st.session_state.previous_filter_state != filter_state:
    st.session_state.expense_page = 1
    st.session_state.previous_filter_state = filter_state

# ============================================================
# Filtering
# ============================================================

filters = [
    Transaction.date >= start_date,
    Transaction.date <= end_date,
]

if show_untagged:
    recently_tagged = st.session_state.recently_tagged_transactions

    if recently_tagged:
        filters.append(
            (~Transaction.tags.any()) | (Transaction.id.in_(recently_tagged))
        )
    else:
        filters.append(~Transaction.tags.any())
elif selected_tags:
    filters.append(Transaction.tags.any(Tag.name.in_(selected_tags)))

# ============================================================
# Stats
# ============================================================

(
    total_transactions,
    debit_total,
    _,
    _,
    _,
    _,
    _,
) = calculate_general_stats(
    filters
)  # TODO: optimization if performance becomes an issue

with stats_placeholder.container():
    stat_col1, stat_col2 = st.columns(2)

    with stat_col1:
        st.metric("Transactions", total_transactions)

    with stat_col2:
        st.metric("Total Expenses", f"${debit_total:,.2f}")

# ============================================================
# Pages Calculation
# ============================================================

total_pages = max(1, (total_transactions + PAGE_SIZE - 1) // PAGE_SIZE)

if st.session_state.expense_page > total_pages:
    st.session_state.expense_page = total_pages

current_page = st.session_state.expense_page
offset = (current_page - 1) * PAGE_SIZE

# ============================================================
# Transactions List
# ============================================================

st.subheader("Transactions")

transactions = get_all_transactions(filters, offset, PAGE_SIZE)

if not transactions:
    st.info("No transactions match your filters.")
else:
    st.divider()

    for transaction in transactions:
        col_date, col_amount, col_description, col_cashback, col_tags = st.columns(
            [1.2, 1, 3, 1, 2.5]
        )

        with col_date:
            st.write(transaction.date.strftime("%b %d, %Y"))

        with col_amount:
            if transaction.direction == TransactionDirection.CREDIT:
                st.markdown(f":green[+${transaction.amount:,.2f}]")
            else:
                st.markdown(f":red[-${transaction.amount:,.2f}]")

        with col_description:
            st.write(transaction.description)

        if transaction.cashback_percentage and transaction.cashback_amount:
            with col_cashback:
                st.caption(
                    f"{transaction.cashback_percentage:,.1f}%"
                    f"→ :green[+${transaction.cashback_amount:,.2f}]"
                )

        with col_tags:
            current_tag_names = [tag.name for tag in transaction.tags]
            widget_key = f"transaction_tags_{transaction.id}"

            st.multiselect(
                label="Tags",
                placeholder="Tags",
                options=tag_names,
                default=current_tag_names,
                key=widget_key,
                label_visibility="collapsed",
                on_change=update_transaction_tags_callback,
                args=(transaction.id, widget_key),
            )

        st.divider()

# ============================================================
# Pagination Controls
# ============================================================

if total_pages > 1:
    col_previous, col_page, col_next = st.columns([1, 2, 1])

    with col_previous:
        if st.button(
            "Previous",
            disabled=current_page <= 1,
            width="content",
        ):
            st.session_state.expense_page -= 1
            st.rerun()

    with col_page:
        st.markdown(
            f"""
            <div style="
                text-align: center;
                padding-top: 8px;
            ">
                Page {current_page} of {total_pages}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_next:
        if st.button(
            "Next",
            disabled=current_page >= total_pages,
            width="content",
        ):
            st.session_state.expense_page += 1
            st.rerun()
