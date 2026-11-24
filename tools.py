"""Simple functions that the agent can call as tools."""
import numpy as np
from config import HOT_DAY_C, LOCATION_NAME
from data_loader import load_data


def get_yearly_stats(year: int) -> str:
    """Get climate statistics for one year: average, hottest and coldest temperature, rain, hot days."""
    df = load_data()
    d = df[df["YEAR"] == year]
    if d.empty:
        return f"No data for {year}. Available years: {df['YEAR'].min()} to {df['YEAR'].max()}."
    hot_days = int((d["T2M_MAX"] >= HOT_DAY_C).sum())
    return (
        f"{LOCATION_NAME}, {year}: "
        f"average temperature {d['T2M'].mean():.2f} C, "
        f"highest daily max {d['T2M_MAX'].max():.1f} C, "
        f"lowest daily min {d['T2M_MIN'].min():.1f} C, "
        f"total rain {d['PRECTOTCORR'].sum():.1f} mm, "
        f"average humidity {d['RH2M'].mean():.1f} %, "
        f"hot days (max >= {HOT_DAY_C} C): {hot_days}."
    )


def get_temperature_trend() -> str:
    """Get the average temperature of every year and the warming trend over the whole data period."""
    df = load_data()
    yearly = df.groupby("YEAR")["T2M"].mean()
    slope = np.polyfit(yearly.index, yearly.values, 1)[0]  # degrees per year
    lines = [f"{year}: {temp:.2f} C" for year, temp in yearly.items()]
    return (
        f"Yearly average temperature in {LOCATION_NAME}:\n" + "\n".join(lines) +
        f"\nLinear trend: {slope * 10:+.2f} C per decade "
        f"(based on only {len(yearly)} years, so this is a rough estimate)."
    )


def get_hottest_days(year: int, how_many: int = 5) -> str:
    """List the hottest days of a given year (highest daily maximum temperature)."""
    df = load_data()
    d = df[df["YEAR"] == year]
    if d.empty:
        return f"No data for {year}. Available years: {df['YEAR'].min()} to {df['YEAR'].max()}."
    top = d.nlargest(how_many, "T2M_MAX")
    lines = [f"{row.DATE:%d %b %Y}: {row.T2M_MAX:.1f} C" for row in top.itertuples()]
    return f"Hottest days in {year} ({LOCATION_NAME}):\n" + "\n".join(lines)


ELECTRICITY_FACTOR = 0.5   # rough average: kg CO2 per kWh
CAR_FACTOR = 0.2           # rough average: kg CO2 per km


def footprint_numbers(electricity_kwh_per_month: float, car_km_per_week: float):
    """Return (electricity, car, total) yearly emissions in kg CO2."""
    electricity = electricity_kwh_per_month * 12 * ELECTRICITY_FACTOR
    car = car_km_per_week * 52 * CAR_FACTOR
    return electricity, car, electricity + car


def calculate_carbon_footprint(electricity_kwh_per_month: float, car_km_per_week: float) -> str:
    """Estimate yearly CO2 emissions (kg) from home electricity and car travel."""
    electricity, car, total = footprint_numbers(electricity_kwh_per_month, car_km_per_week)
    return (
        f"Estimated yearly footprint: {total:.0f} kg CO2 "
        f"(electricity: {electricity:.0f} kg, car: {car:.0f} kg). "
        "This is a rough estimate based on average emission factors."
    )
