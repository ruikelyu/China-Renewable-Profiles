# 中国分省逐小时风光出力因子（2020 气象年） / China provincial hourly wind & solar capacity factors (weather year 2020)

## Files

| File | Content | Shape |
|---|---|---|
| `solar_cf_2020.csv` | 光伏 PV capacity factor | 8784 h × 31 provinces |
| `onwind_cf_2020.csv` | 陆上风电 onshore wind capacity factor | 8784 h × 31 provinces |
| `offwind_cf_2020.csv` | 海上风电 offshore wind capacity factor | 8784 h × 11 coastal provinces |
| `provincial_cf_2020.nc` | All three in one NetCDF (`time × province`, offwind = NaN inland), with Chinese names in `province_zh` | — |
| `provincial_summary_2020.csv` | Per province & tech: technical potential `p_nom_max_MW`, mean CF, full-load hours | 73 rows |

- **Unit:** per-unit of installed capacity (0–1). Hourly output (MW) = CF × installed capacity (MW).
- **Time:** **Beijing time (UTC+8)**, hourly, 2020-01-01 00:00 → 2020-12-31 23:00 (8784 h, leap year).
  To get UTC: `df.index - pd.Timedelta(hours=8)`.
- **Provinces:** 31 mainland provinces (English pinyin names; Inner Mongolia = `InnerMongolia`). Hong Kong, Macao and Taiwan are not included.

## Method

Generated with [Atlite](https://atlite.readthedocs.io/) from **ERA5** reanalysis (0.25° × 0.25°, hourly, 2020)
in [PyPSA-China-THU](https://github.com/ruikelyu/PyPSA-China-THU) (`resources/profile_*.nc`), then exported by
`scripts/export_provincial_profiles.py`.

| Tech | Model | Settings |
|---|---|---|
| Solar | Crystalline Si (`CSi`) | slope 35°, azimuth 180° (south), correction factor 0.85 |
| Onshore wind | Vestas V112 3 MW | — |
| Offshore wind | NREL Reference Turbine 5 MW offshore | correction factor 0.8855, water depth ≤ 50 m |

Each provincial series is the **capacity-weighted average over all land-eligible ERA5 cells** in the province
(weights ∝ available area × `capacity_per_sqkm`: solar 5.1, onshore 3, offshore 2 MW/km²). `p_nom_max_MW` is
the resulting technical potential, not installed capacity.

## Caveats

- **This is a resource profile, not observed generation.** It reflects where capacity *could* be built, not
  where it actually is, and does not include curtailment, outages or grid constraints.
- **Onshore wind is low in many inland/mountainous provinces** (e.g. Shanxi, Gansu, Sichuan, Chongqing) relative to
  reported 2020 utilization hours (~2000 h national average). ERA5 is known to underestimate wind speed in complex
  terrain, and the area-weighted average includes many low-wind cells. Consider rescaling to reported utilization
  hours (e.g. CEC / NEA statistics) if absolute energy matters; the hourly *shape* is more reliable than the level.
- **Solar** full-load hours (≈820–1720 h) are in the range of reported values; the 0.85 factor accounts for system losses.
- **Other years:** a common practice is to combine installed capacity of the target year with these 2020 per-unit
  profiles (2020 as reference weather year). Inter-annual weather variability is not captured.

## Verification

`python scripts/check_provincial_profiles.py` checks shape, NaN, range, timezone (solar is zero at night; solar
peak moves later from Heilongjiang → Anhui → Xinjiang), NetCDF/CSV consistency, and correlation with the
city-level Anhui series in `data/resources/` (PV r = 0.998, wind r = 0.993).

## License & citation

Data: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Contains modified Copernicus Climate Change
Service information (ERA5, 2020). Please cite this repository (Ruike Lyu, *China Renewable Profiles*,
https://github.com/ruikelyu/China-Renewable-Profiles) and ERA5 (Hersbach et al., 2020, QJRMS, doi:10.1002/qj.3803).
