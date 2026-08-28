import streamlit as st

import components.charts.general_stats
import components.charts.expenses_by_tag
import components.charts.spending_over_time
import components.charts.monthly_spending

from services.transactions_service import get_min_max_dates

st.set_page_config(layout="wide")

st.title("Dashboard")

min_date, max_date = get_min_max_dates()

if min_date is None:
    st.info("No transactions yet. " "Import transactions or add one manually.")
    st.stop()

filter_col1, filter_col2 = st.columns(2)

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

if start_date > end_date:
    st.error("The start date must be before the end date.")
    st.stop()

components.charts.general_stats.draw(start_date, end_date)
components.charts.expenses_by_tag.draw(start_date, end_date)
components.charts.spending_over_time.draw(start_date, end_date)
components.charts.monthly_spending.draw(start_date, end_date)
