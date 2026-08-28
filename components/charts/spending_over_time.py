import streamlit as st

from models import Transaction
from services.stats_service import calculate_daily_spending
from components.charts.colors import ROSE


def draw(start_date, end_date):
    st.subheader("Spending Over Time")

    filters = [
        Transaction.date >= start_date,
        Transaction.date <= end_date,
    ]
    daily_dates, daily_amounts = calculate_daily_spending(filters)

    if daily_dates and daily_amounts:
        st.plotly_chart(
            {
                "data": [
                    {
                        "type": "scatter",
                        "x": daily_dates,
                        "y": daily_amounts,
                        "mode": "lines",
                        "line": {
                            "color": ROSE,
                            "width": 3,
                            "shape": "linear",
                        },
                        "hovertemplate": (
                            "<b>%{x}</b><br>" "$%{y:,.2f}" "<extra></extra>"
                        ),
                    }
                ],
                "layout": {
                    "height": 400,
                    "margin": {
                        "l": 20,
                        "r": 20,
                        "t": 20,
                        "b": 20,
                    },
                    "xaxis": {
                        "title": None,
                    },
                    "yaxis": {
                        "title": "Amount",
                    },
                    "paper_bgcolor": ("rgba(0,0,0,0)"),
                    "plot_bgcolor": ("rgba(0,0,0,0)"),
                    "hovermode": "x unified",
                    "dragmode": False,
                },
            },
            width="stretch",
            config={
                "displayModeBar": False,
                "scrollZoom": False,
                "doubleClick": False,
            },
        )
    else:
        st.info("No expense data for this period.")
