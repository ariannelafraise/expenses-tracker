import streamlit as st

from services.stats_service import calculate_spending_per_tag
from models import Transaction
from components.charts.colors import PASTEL_COLORS


def draw(start_date, end_date):
    st.subheader("Expenses by Tag")
    filters = [
        Transaction.date >= start_date,
        Transaction.date <= end_date,
    ]
    draw_pie_chart(calculate_spending_per_tag(filters))


def draw_pie_chart(spending_per_tag_stats):
    if spending_per_tag_stats:
        tag_amounts = [float(row.amount) for row in spending_per_tag_stats]
        tag_names = [row.name for row in spending_per_tag_stats]
        total_tag_spending = sum(tag_amounts)

        # Only show text inside sufficiently large slices.
        # All tags remain visible in the legend.
        slice_text = [
            (
                (
                    f"{row.name}<br>"
                    f"{(float(row.amount) / total_tag_spending) * 100:.1f}%"
                )
                if (float(row.amount) / total_tag_spending >= 0.05)
                else ""
            )
            for row in spending_per_tag_stats
        ]

        colors = [
            PASTEL_COLORS[index % len(PASTEL_COLORS)]
            for index in range(len(spending_per_tag_stats))
        ]

        st.plotly_chart(
            {
                "data": [
                    {
                        "type": "pie",
                        "labels": tag_names,
                        "values": tag_amounts,
                        "text": slice_text,
                        # Only the larger slices get text.
                        # Small slices have no text on the pie.
                        "textinfo": "text",
                        "textposition": "inside",
                        "insidetextorientation": "horizontal",
                        "marker": {
                            "colors": colors,
                            "line": {
                                "width": 1,
                                "color": ("rgba(0,0,0,0)"),
                            },
                        },
                        "hole": 0.48,
                        "hovertemplate": (
                            "<b>%{label}</b><br>"
                            "$%{value:,.2f}<br>"
                            "%{percent}"
                            "<extra></extra>"
                        ),
                    }
                ],
                "layout": {
                    "height": 450,
                    "margin": {
                        "l": 20,
                        "r": 20,
                        "t": 20,
                        "b": 20,
                    },
                    "showlegend": True,
                    "legend": {
                        "orientation": "h",
                        "y": -0.05,
                        "x": 0.5,
                        "xanchor": "center",
                    },
                    "paper_bgcolor": ("rgba(0,0,0,0)"),
                    "plot_bgcolor": ("rgba(0,0,0,0)"),
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
        st.info("No tagged expenses for this period.")
