"""Sanity checks for data/provincial/. Run from the repo root:

    python scripts/check_provincial_profiles.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

D = Path("data/provincial")
EXPECTED_COLS = {"solar": 31, "onwind": 31, "offwind": 11}


def load(tech):
    return pd.read_csv(D / f"{tech}_cf_2020.csv", index_col=0, parse_dates=True)


def main():
    cf = {t: load(t) for t in EXPECTED_COLS}

    for t, df in cf.items():
        assert df.shape == (8784, EXPECTED_COLS[t]), (t, df.shape)
        assert df.index.is_monotonic_increasing and df.index.is_unique, t
        assert (df.index[1:] - df.index[:-1] == pd.Timedelta("1h")).all(), t
        assert not df.isna().any().any(), f"{t}: NaN"
        assert df.min().min() >= 0 and df.max().max() <= 1, f"{t}: out of [0,1]"
    print("shape / index / NaN / range: OK")

    # Solar must be zero in the middle of the night (Beijing time)
    night = cf["solar"].between_time("01:00", "03:00")
    assert night.max().max() == 0, "solar non-zero at night -> timezone problem"

    # Solar noon must move later going west (Heilongjiang ~127E -> Xinjiang ~87E)
    peak = cf["solar"].groupby(cf["solar"].index.hour).mean().idxmax()
    assert peak["Heilongjiang"] < peak["Anhui"] < peak["Xinjiang"], peak
    print(f"timezone (solar peak hour HLJ/AH/XJ = {peak['Heilongjiang']}/{peak['Anhui']}/{peak['Xinjiang']}): OK")

    # NetCDF matches CSVs
    ds = xr.open_dataset(D / "provincial_cf_2020.nc")
    for t, df in cf.items():
        nc = ds[t].to_pandas()[df.columns]
        assert np.allclose(nc.values, df.values, atol=1e-4), t
    print("NetCDF == CSV: OK")

    # Cross-check against the city-level Anhui series in this repo
    for t, f in [("solar", "anhui_pv_factors_2020.csv"), ("onwind", "anhui_wind_factors_2020.csv")]:
        p = Path("data/resources") / f
        if p.exists():
            city = pd.read_csv(p, index_col=0, parse_dates=True).mean(axis=1)
            r = np.corrcoef(city.values, cf[t]["Anhui"].values)[0, 1]
            assert r > 0.95, (t, r)
            print(f"Anhui {t} vs city-average CSV: corr={r:.3f}, "
                  f"mean {cf[t]['Anhui'].mean():.3f} vs {city.mean():.3f}")

    print("\nFull-load hours (h/yr):")
    print(pd.DataFrame({t: df.sum() for t, df in cf.items()}).round(0).to_string())


if __name__ == "__main__":
    main()
