"""Export provincial hourly capacity factors (2020 weather year) to ready-to-use files.

Source: the Atlite-generated `profile_{solar,onwind,offwind}.nc` files of PyPSA-China-THU
(https://github.com/ruikelyu/PyPSA-China-THU, `resources/`).

Usage (from the repo root, in an env with xarray + pandas + netCDF4/h5netcdf):

    python scripts/export_provincial_profiles.py --src /path/to/PyPSA-China-THU/resources

Outputs go to data/provincial/.
"""
import argparse
from pathlib import Path

import pandas as pd
import xarray as xr

TECHS = {"solar": "solar", "onwind": "onwind", "offwind": "offwind"}

PROVINCES_ZH = {
    "Anhui": "安徽", "Beijing": "北京", "Chongqing": "重庆", "Fujian": "福建",
    "Gansu": "甘肃", "Guangdong": "广东", "Guangxi": "广西", "Guizhou": "贵州",
    "Hainan": "海南", "Hebei": "河北", "Heilongjiang": "黑龙江", "Henan": "河南",
    "Hubei": "湖北", "Hunan": "湖南", "InnerMongolia": "内蒙古", "Jiangsu": "江苏",
    "Jiangxi": "江西", "Jilin": "吉林", "Liaoning": "辽宁", "Ningxia": "宁夏",
    "Qinghai": "青海", "Shaanxi": "陕西", "Shandong": "山东", "Shanghai": "上海",
    "Shanxi": "山西", "Sichuan": "四川", "Tianjin": "天津", "Tibet": "西藏",
    "Xinjiang": "新疆", "Yunnan": "云南", "Zhejiang": "浙江",
}


def main(src: Path, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    data_vars, potentials = {}, []

    for tech, fname in TECHS.items():
        ds = xr.open_dataset(src / f"profile_{fname}.nc")
        cf = ds["profile"].transpose("time", "bus").to_pandas()
        if cf.index.tz is not None:
            cf.index = cf.index.tz_localize(None)
        cf.index.name = "time"  # Beijing time (UTC+8), hour-labelled
        cf.columns.name = None
        cf = cf.clip(lower=0.0, upper=1.0)

        cf.round(4).to_csv(out / f"{tech}_cf_2020.csv")
        data_vars[tech] = cf.rename_axis(columns="province")

        potentials.append(
            pd.DataFrame({
                "tech": tech,
                "province": ds["bus"].values,
                "p_nom_max_MW": ds["p_nom_max"].values.round(1),
                "mean_cf": cf.mean().values.round(4),
                "full_load_hours": (cf.sum()).values.round(0),
            })
        )

    # One NetCDF with all techs on a common province axis (offwind NaN for inland provinces)
    provinces = sorted(PROVINCES_ZH)
    ds_out = xr.Dataset({
        tech: xr.DataArray(df.reindex(columns=provinces), dims=("time", "province"))
        for tech, df in data_vars.items()
    })
    ds_out = ds_out.assign_coords(province_zh=("province", [PROVINCES_ZH[p] for p in provinces]))
    for tech in ds_out.data_vars:
        ds_out[tech].attrs = {"units": "p.u. of installed capacity", "long_name": f"{tech} hourly capacity factor"}
    ds_out["time"].attrs = {"timezone": "Asia/Shanghai (UTC+8)"}
    ds_out.attrs = {
        "title": "China provincial hourly wind & solar capacity factors, weather year 2020",
        "source": "ERA5 reanalysis via Atlite; profiles from PyPSA-China-THU",
        "license": "CC-BY-4.0",
    }
    enc = {v: {"zlib": True, "complevel": 4, "dtype": "float32"} for v in ds_out.data_vars}
    ds_out.to_netcdf(out / "provincial_cf_2020.nc", encoding=enc)

    summary = pd.concat(potentials, ignore_index=True)
    summary.insert(2, "province_zh", summary["province"].map(PROVINCES_ZH))
    summary.to_csv(out / "provincial_summary_2020.csv", index=False, encoding="utf-8-sig")

    print(f"Wrote {len(list(out.iterdir()))} files to {out}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--src", type=Path, required=True, help="PyPSA-China-THU/resources directory")
    p.add_argument("--out", type=Path, default=Path("data/provincial"))
    a = p.parse_args()
    main(a.src, a.out)
