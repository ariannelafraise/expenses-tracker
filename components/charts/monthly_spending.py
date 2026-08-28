import streamlit as st

from models import Transaction
from services.stats_service import calculate_monthly_spending
from components.charts.colors import PINK_LIGHT


def draw(start_date, end_date):
    st.subheader("Monthly Spending")

    filters = [
        Transaction.date >= start_date,
        Transaction.date <= end_date,
    ]
    monthly_spending = calculate_monthly_spending(filters)
    if monthly_spending:
        months = [row.month for row in monthly_spending]
        amounts = [float(row.amount) for row in monthly_spending]

        st.plotly_chart(
            {
                "data": [
                    {
                        "type": "bar",
                        "x": months,
                        "y": amounts,
                        "marker": {
                            "color": PINK_LIGHT,
                            "line": {
                                "width": 0,
                            },
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
                    "bargap": 0.35,
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
        st.info("No monthly expense data for this period.")
