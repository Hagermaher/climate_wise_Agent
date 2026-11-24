"""Dashboard page and carbon calculator page."""
import pandas as pd
import streamlit as st

from config import HOT_DAY_C, LOCATION_NAME
from data_loader import load_data
from tools import footprint_numbers


def show_dashboard():
    df = load_data()
    years = [int(y) for y in sorted(df["YEAR"].unique())]
    year = st.select_slider("Choose a year", options=years, value=years[-1])

    yearly = df.groupby("YEAR").agg(
        avg_temp=("T2M", "mean"),
        max_temp=("T2M_MAX", "max"),
        rain=("PRECTOTCORR", "sum"),
        hot_days=("T2M_MAX", lambda s: int((s >= HOT_DAY_C).sum())),
    )
    cur = yearly.loc[year]
    prev = yearly.loc[year - 1] if (year - 1) in yearly.index else None

    def delta(key, unit, fmt):
        return None if prev is None else f"{cur[key] - prev[key]:{fmt}} {unit} vs {year - 1}"

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Average temperature", f"{cur.avg_temp:.2f} °C", delta("avg_temp", "°C", "+.2f"), delta_color="inverse")
    c2.metric("Highest temperature", f"{cur.max_temp:.1f} °C")
    c3.metric(f"Hot days (≥ {HOT_DAY_C} °C)", f"{int(cur.hot_days)}", delta("hot_days", "days", "+.0f"), delta_color="inverse")
    c4.metric("Total rain", f"{cur.rain:.0f} mm", delta("rain", "mm", "+.0f"), delta_color="off")

    left, right = st.columns(2)
    with left:
        st.subheader("Average temperature by year (°C)")
        st.line_chart(yearly["avg_temp"])
    with right:
        st.subheader(f"Hot days per year (≥ {HOT_DAY_C} °C)")
        st.bar_chart(yearly["hot_days"])

    monthly = df[df["YEAR"] == year].groupby("MONTH").agg(avg_temp=("T2M", "mean"), rain=("PRECTOTCORR", "sum"))
    left, right = st.columns(2)
    with left:
        st.subheader(f"{year}: average temperature by month (°C)")
        st.line_chart(monthly["avg_temp"])
    with right:
        st.subheader(f"{year}: rain by month (mm)")
        st.bar_chart(monthly["rain"])

    st.caption(f"NASA POWER daily data for {LOCATION_NAME}. The record is short (11 years), so it cannot show a long-term trend by itself.")


def show_carbon_calculator():
    st.subheader("🌱 Carbon footprint calculator")
    kwh = st.slider("Electricity (kWh per month)", 0, 1500, 300, step=10)
    km = st.slider("Car travel (km per week)", 0, 1000, 100, step=10)

    electricity, car, total = footprint_numbers(kwh, km)
    c1, c2, c3 = st.columns(3)
    c1.metric("Total per year", f"{total:,.0f} kg CO₂")
    c2.metric("Electricity", f"{electricity:,.0f} kg CO₂")
    c3.metric("Car", f"{car:,.0f} kg CO₂")

    st.bar_chart(pd.DataFrame({"kg CO₂ per year": [electricity, car]}, index=["Electricity", "Car"]))

    if total > 0:
        if electricity >= car:
            st.info("Your biggest source is electricity. LED lamps and efficient appliances can reduce it.")
        else:
            st.info("Your biggest source is car travel. Public transport or sharing rides for some trips can reduce it.")
    st.caption("Rough estimate using average factors: 0.5 kg CO₂ per kWh and 0.2 kg CO₂ per km.")
