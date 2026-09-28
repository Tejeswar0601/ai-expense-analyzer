"""
Reusable Plotly chart builders.

Each function takes the report data (already computed by the backend's
analysis_service) and returns a Plotly Figure - no calculation happens
here, only visualization.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def category_bar_chart(category_analysis: list[dict]) -> go.Figure:
    """Bar chart: total spending per category."""
    df = pd.DataFrame(category_analysis)
    fig = px.bar(
        df,
        x="category",
        y="total",
        text="total",
        labels={"category": "Category", "total": "Amount (₹)"},
        title="Category-wise Spending",
    )
    fig.update_traces(texttemplate="₹%{text:,.0f}", textposition="outside")
    fig.update_layout(margin=dict(t=50, b=20))
    return fig


def category_pie_chart(category_analysis: list[dict]) -> go.Figure:
    """Donut chart: category distribution as a percentage of total."""
    df = pd.DataFrame(category_analysis)
    fig = px.pie(
        df,
        names="category",
        values="total",
        hole=0.45,
        title="Category Distribution",
    )
    fig.update_traces(textinfo="percent+label")
    fig.update_layout(margin=dict(t=50, b=20))
    return fig


def daily_spending_line_chart(daily_totals: list[dict]) -> go.Figure:
    """Line chart: spending per day across the month."""
    df = pd.DataFrame(daily_totals)
    df["date"] = pd.to_datetime(df["date"])
    fig = px.line(
        df,
        x="date",
        y="total",
        markers=True,
        labels={"date": "Date", "total": "Amount (₹)"},
        title="Daily Spending",
    )
    fig.update_layout(margin=dict(t=50, b=20))
    return fig


def weekly_spending_bar_chart(weekly_totals: list[dict]) -> go.Figure:
    """Bar chart: spending per week of the month."""
    df = pd.DataFrame(weekly_totals)
    fig = px.bar(
        df,
        x="week",
        y="total",
        text="total",
        labels={"week": "Week", "total": "Amount (₹)"},
        title="Weekly Spending",
    )
    fig.update_traces(texttemplate="₹%{text:,.0f}", textposition="outside")
    fig.update_layout(margin=dict(t=50, b=20))
    return fig
