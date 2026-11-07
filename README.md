# China Renewable Profiles: Provincial Hourly Wind & Solar Capacity Factors

**English** | [中文](README_zh.md)

Ready-to-use **hourly capacity factors for solar PV, onshore wind and offshore wind in 31 Chinese provinces**,
computed from ERA5 reanalysis (weather year 2020) with [Atlite](https://atlite.readthedocs.io/). Clone the repo
and use the CSVs directly: no reanalysis download, no conda environment.

The repo also contains scripts to regenerate the data or extract point-level profiles, plus a small MATLAB
microgrid reliability model.

---

## Contents

| | What | Where | Needs |
|---|---|---|---|
| ① | **Provincial hourly capacity factors** (main dataset) | [`data/provincial/`](data/provincial/) | nothing (CSV) |
| ② | City-level example: 16 cities in Anhui | [`data/resources/`](data/resources/) | nothing (CSV) |
| ③ | Scripts to regenerate gridded data and extract any lat/lon | [`scripts/`](scripts/) | conda env + ERA5 download |
| ④ | MATLAB microgrid reliability simulation (LOLP / EDNS) | [`simulation/`](simulation/) | MATLAB + YALMIP + CPLEX |

## Quick start

```python
import pandas as pd

solar  = pd.read_csv("data/provincial/solar_cf_2020.csv",  index_col=0, parse_dates=True)
onwind = pd.read_csv("data/provincial/onwind_cf_2020.csv", index_col=0, parse_dates=True)

# capacity factor × installed capacity (MW) = hourly output (MW)
anhui_pv_MW = solar["Anhui"] * 40_000
```

See [`scripts/example_usage.py`](scripts/example_usage.py) for annual energy, daily profiles and monthly means.

## The dataset

| File | Content | Size |
|---|---|---|
| [`solar_cf_2020.csv`](data/provincial/solar_cf_2020.csv) | Solar PV | 8784 h × 31 provinces |
| [`onwind_cf_2020.csv`](data/provincial/onwind_cf_2020.csv) | Onshore wind | 8784 h × 31 provinces |
| [`offwind_cf_2020.csv`](data/provincial/offwind_cf_2020.csv) | Offshore wind | 8784 h × 11 coastal provinces |
| [`provincial_cf_2020.nc`](data/provincial/provincial_cf_2020.nc) | All three in one NetCDF, with Chinese names | — |
| [`provincial_summary_2020.csv`](data/provincial/provincial_summary_2020.csv) | Technical potential (MW), mean CF, full-load hours | 73 rows |

- **Unit:** per-unit of installed capacity, 0–1.
- **Time:** hourly, **Beijing time (UTC+8)**, 2020-01-01 00:00 to 2020-12-31 23:00 (leap year, 8784 h).
- **Spatial:** each province is the capacity-weighted average over its land-eligible ERA5 cells (0.25°, ≈ 30 km).
- **Technology:** crystalline-Si PV (35° tilt, south-facing), Vestas V112 3 MW onshore, NREL 5 MW offshore.

Full method, parameters and verification: [`data/provincial/METADATA.md`](data/provincial/METADATA.md).

### Before you use it

- These are **resource profiles**, not observed generation: no curtailment, outages or grid limits.
- **Onshore wind is low in many inland and mountainous provinces** (e.g. Shanxi, Gansu, Sichuan) compared with
  reported 2020 utilization hours. Trust the hourly *shape* more than the *level*, and rescale to official
  statistics if absolute energy matters.
- Solar full-load hours (≈ 820–1720 h/yr) are in line with reported values.

## FAQ

**Only 2020? What about other years?**
Weather varies relatively little from year to year; installed capacity is what changes. A common approach is to
combine the target year's installed capacity with these 2020 per-unit profiles, treating 2020 as the reference
weather year. Inter-annual weather variability is not captured.

**The Tsinghua cloud link in the old README is dead.**
Yes. The provincial data now lives in this repository. For gridded data (any lat/lon or city), regenerate it as
described below.

**Can I get city-level or point-level profiles?**
Yes, via the gridded workflow below. Anhui's 16 prefecture-level cities are already included in
`data/resources/anhui_{pv,wind}_factors_2020.csv`.

## Advanced: gridded data and point extraction

The gridded national files (`wind_factor-china-2020.nc`, `pv_factor-china-2020.nc`) are large and not
version-controlled. To rebuild them:

```bash
conda env create -f environment.yaml
conda activate pypsa-china
```

> `environment.yaml` was exported on Windows. On macOS or Linux, install `atlite xarray pandas netcdf4` from
> conda-forge instead.

1. Configure the [Copernicus CDS API](https://cds.climate.copernicus.eu/how-to-api).
2. Download ERA5 (`cutouts/China-2020.nc`, slow) and compute gridded capacity factors:
   ```bash
   python scripts/build_renewable_profile.py
   ```
3. Extract any locations (edit the lat/lon list in the script; Anhui cities are the example):
   ```bash
   python scripts/extract_renewable_factor.py
   ```

The provincial dataset is rebuilt from PyPSA-China-THU outputs with
`python scripts/export_provincial_profiles.py --src <PyPSA-China-THU>/resources` and verified with
`python scripts/check_provincial_profiles.py`.

> The gridded workflow uses a 45° PV tilt and no loss factor. The provincial dataset uses 35° and a 0.85 loss
> factor, so the two are not identical.

## MATLAB microgrid reliability simulation

[`simulation/`](simulation/) is a simplified, teaching-oriented model of a microgrid with wind, PV, a thermal
unit and storage. For each Monte Carlo sample it:

- draws one day of wind speed (Weibull, with speed-dependent turbine outages) and irradiance (Beta distribution,
  sunny, cloudy or rainy weather types);
- solves an economic dispatch at 15-min resolution (96 steps) as a mixed-integer QP;
- records unserved energy, then reports **LOLP** and **EDNS** across increasing wind and PV penetration.

Run `pre.m` (main loop), which calls `micro_grid.m` (one dispatch). Requires MATLAB,
[YALMIP](https://yalmip.github.io/) and CPLEX (or switch the solver in `micro_grid.m`, e.g. to Gurobi).

> Source comments are GBK-encoded and may look garbled on GitHub. Open them in MATLAB with Chinese locale or
> convert with `iconv -f GBK -t UTF-8`.

The model is not calibrated against real systems; for accurate resource estimates use the Atlite-based data above.

## Repository layout

```
data/
  provincial/        ← main dataset (CSV + NetCDF + METADATA + LICENSE)
  resources/         Anhui city-level example
scripts/
  export_provincial_profiles.py   build data/provincial from PyPSA-China-THU
  check_provincial_profiles.py    sanity checks
  example_usage.py                how to use the data
  build_renewable_profile.py      ERA5 → gridded CF (Atlite)
  extract_renewable_factor.py     gridded CF → any lat/lon
simulation/          MATLAB microgrid reliability model
environment.yaml     conda environment (Windows export)
```

## Citation & license

If you use the data, please cite this repository and ERA5:

- Ruike Lyu, *China Renewable Profiles*, https://github.com/ruikelyu/China-Renewable-Profiles
- Hersbach, H. et al. (2020). The ERA5 global reanalysis. *QJRMS*, 146, 1999–2049. doi:10.1002/qj.3803

Data in `data/provincial/` is licensed under [CC BY 4.0](data/provincial/LICENSE) and contains modified Copernicus
Climate Change Service information.

Related: [PyPSA-China-THU](https://github.com/ruikelyu/PyPSA-China-THU), a provincial PyPSA capacity-expansion model
of China that uses these profiles.

Questions and data requests: please [open an issue](https://github.com/ruikelyu/China-Renewable-Profiles/issues).
