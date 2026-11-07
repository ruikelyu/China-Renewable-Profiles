"""Minimal example: load provincial capacity factors and turn them into hourly generation.

    python scripts/example_usage.py
"""
import pandas as pd

solar = pd.read_csv("data/provincial/solar_cf_2020.csv", index_col=0, parse_dates=True)
onwind = pd.read_csv("data/provincial/onwind_cf_2020.csv", index_col=0, parse_dates=True)

# Hourly generation (MW) for an assumed installed capacity (MW) — replace with your own scenario
installed = {"solar": 40_000, "onwind": 8_000}
province = "Anhui"
gen = pd.DataFrame({
    "solar_MW": solar[province] * installed["solar"],
    "onwind_MW": onwind[province] * installed["onwind"],
})

print(f"{province}: annual energy (TWh)")
print((gen.sum() / 1e6).round(2))
print("\nAverage daily profile (MW, Beijing time):")
print(gen.groupby(gen.index.hour).mean().round(0))

# Resample to daily / monthly if needed
print("\nMonthly mean CF:")
print(pd.DataFrame({"solar": solar[province], "onwind": onwind[province]}).resample("MS").mean().round(3))
