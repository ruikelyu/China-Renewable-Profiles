# 中国可再生能源出力曲线：分省逐小时风光出力因子

[English](README.md) | **中文**

本仓库提供**中国 31 个省份光伏、陆上风电、海上风电的逐小时出力因子**，基于 ERA5 再分析气象数据（2020 气象年），
使用 [Atlite](https://atlite.readthedocs.io/) 计算。克隆仓库后可直接使用 CSV，无需下载气象数据或配置环境。

仓库还包含重新生成数据、提取任意地点出力的脚本，以及一个 MATLAB 微电网可靠性仿真模型。

---

## 内容一览

| | 内容 | 位置 | 需要 |
|---|---|---|---|
| ① | **分省逐小时出力因子**（核心数据） | [`data/provincial/`](data/provincial/) | 无（CSV） |
| ② | 地级市示例：安徽省 16 个地级市 | [`data/resources/`](data/resources/) | 无（CSV） |
| ③ | 重新生成网格数据、提取任意经纬度的脚本 | [`scripts/`](scripts/) | conda 环境 + ERA5 下载 |
| ④ | MATLAB 微电网可靠性仿真（LOLP / EDNS） | [`simulation/`](simulation/) | MATLAB + YALMIP + CPLEX |

## 快速开始

```python
import pandas as pd

solar  = pd.read_csv("data/provincial/solar_cf_2020.csv",  index_col=0, parse_dates=True)
onwind = pd.read_csv("data/provincial/onwind_cf_2020.csv", index_col=0, parse_dates=True)

# 出力因子 × 装机容量 (MW) = 逐小时出力 (MW)
anhui_pv_MW = solar["Anhui"] * 40_000
```

年发电量、典型日曲线、月均值等示例见 [`scripts/example_usage.py`](scripts/example_usage.py)。

## 数据说明

| 文件 | 内容 | 规模 |
|---|---|---|
| [`solar_cf_2020.csv`](data/provincial/solar_cf_2020.csv) | 光伏 | 8784 小时 × 31 省 |
| [`onwind_cf_2020.csv`](data/provincial/onwind_cf_2020.csv) | 陆上风电 | 8784 小时 × 31 省 |
| [`offwind_cf_2020.csv`](data/provincial/offwind_cf_2020.csv) | 海上风电 | 8784 小时 × 11 个沿海省份 |
| [`provincial_cf_2020.nc`](data/provincial/provincial_cf_2020.nc) | 以上三者合并的 NetCDF（含中文省名） | — |
| [`provincial_summary_2020.csv`](data/provincial/provincial_summary_2020.csv) | 各省技术可开发潜力 (MW)、年均出力因子、年利用小时数 | 73 行 |

- **单位：** 装机容量的标么值，0–1。
- **时间：** 逐小时，**北京时间（UTC+8）**，2020-01-01 00:00 至 2020-12-31 23:00（闰年，8784 小时）。
- **空间：** 每个省份为省内所有可开发 ERA5 网格（0.25°，约 30 km）按可装机容量加权的平均值。
- **技术参数：** 晶硅光伏（倾角 35°，朝南），陆上风机 Vestas V112 3 MW，海上风机 NREL 5 MW。
- **省份名称：** 使用英文拼音（内蒙古为 `InnerMongolia`）；中英文对照见 summary 文件或 NetCDF 中的 `province_zh`。

完整的方法、参数和校验结果见 [`data/provincial/METADATA.md`](data/provincial/METADATA.md)。

### 使用前请注意

- 这是**资源出力曲线**，不是实际发电数据：不含弃风弃光、机组故障和电网约束。
- **不少内陆和山区省份的陆上风电偏低**（如山西、甘肃、四川），低于 2020 年实际利用小时数。主要原因是 ERA5 在复杂地形下低估风速，
  且省级平均包含了大量低风速网格。建议更看重逐小时的**形状**而非**绝对水平**；如需准确的发电量，可按官方统计的利用小时数进行缩放。
- 光伏年利用小时数（约 820–1720 小时）与实际统计值基本一致。

## 常见问题

**只有 2020 年的数据吗？其他年份怎么办？**
每年的气象条件差别不大，主要是装机不同。常见做法是用目标年份的装机容量乘以 2020 年的标么值，即"以 2020 年为基准气象年"。
这种做法无法反映年际气象差异。

**旧版 README 中的清华云盘链接失效了？**
是的。分省数据现已直接放在仓库中。如需网格数据（任意经纬度或地级市），请按下文方法自行生成。

**能获取地级市或某个具体地点的出力吗？**
可以，使用下文的网格数据流程。安徽省 16 个地级市的结果已放在 `data/resources/anhui_{pv,wind}_factors_2020.csv`。

## 进阶：网格数据与任意地点提取

全国网格数据（`wind_factor-china-2020.nc`、`pv_factor-china-2020.nc`）体积较大，未放入仓库。重新生成方法：

```bash
conda env create -f environment.yaml
conda activate pypsa-china
```

> `environment.yaml` 导出自 Windows。在 macOS 或 Linux 上，请改为从 conda-forge 安装 `atlite xarray pandas netcdf4`。

1. 配置 [Copernicus CDS API](https://cds.climate.copernicus.eu/how-to-api)。
2. 下载 ERA5 数据（`cutouts/China-2020.nc`，耗时较长）并计算网格出力因子：
   ```bash
   python scripts/build_renewable_profile.py
   ```
3. 提取任意地点（修改脚本中的经纬度列表，默认以安徽各地级市为例）：
   ```bash
   python scripts/extract_renewable_factor.py
   ```

分省数据由 PyPSA-China-THU 的计算结果导出：
`python scripts/export_provincial_profiles.py --src <PyPSA-China-THU>/resources`，并用
`python scripts/check_provincial_profiles.py` 校验。

> 网格数据流程中光伏倾角为 45°、未乘损耗系数；分省数据为 35°、损耗系数 0.85，两者结果不完全相同。

## MATLAB 微电网可靠性仿真

[`simulation/`](simulation/) 是一个简化的、偏教学用途的微电网模型，包含风电、光伏、火电机组和储能。每次蒙特卡洛抽样：

- 随机生成一天的风速（威布尔分布，风机故障率随风速变化）和光照（Beta 分布，分晴天、阴天、雨天）；
- 以 15 分钟为步长（96 个时段）求解混合整数二次规划的经济调度；
- 记录缺电量，最终给出不同风光渗透率下的 **LOLP**（失负荷概率）和 **EDNS**（期望缺供电力）。

运行 `pre.m`（主循环），它会调用 `micro_grid.m`（单次调度）。需要 MATLAB、[YALMIP](https://yalmip.github.io/) 和 CPLEX
（也可在 `micro_grid.m` 中改用 Gurobi 等求解器）。

> 源码注释为 GBK 编码，在 GitHub 上可能显示乱码。请在中文环境的 MATLAB 中打开，或用 `iconv -f GBK -t UTF-8` 转换。

该模型未经实际系统标定；如需准确的资源评估，请使用上文基于 Atlite 的数据。

## 目录结构

```
data/
  provincial/        ← 核心数据（CSV + NetCDF + METADATA + LICENSE）
  resources/         安徽地级市示例
scripts/
  export_provincial_profiles.py   由 PyPSA-China-THU 导出分省数据
  check_provincial_profiles.py    数据校验
  example_usage.py                使用示例
  build_renewable_profile.py      ERA5 → 网格出力因子（Atlite）
  extract_renewable_factor.py     网格出力因子 → 任意经纬度
simulation/          MATLAB 微电网可靠性模型
environment.yaml     conda 环境（Windows 导出）
```

## 引用与许可

如使用本数据，请引用本仓库及 ERA5：

- Ruike Lyu, *China Renewable Profiles*, https://github.com/ruikelyu/China-Renewable-Profiles
- Hersbach, H. et al. (2020). The ERA5 global reanalysis. *QJRMS*, 146, 1999–2049. doi:10.1002/qj.3803

`data/provincial/` 中的数据采用 [CC BY 4.0](data/provincial/LICENSE) 许可，包含经修改的 Copernicus 气候变化服务信息。

相关项目：[PyPSA-China-THU](https://github.com/ruikelyu/PyPSA-China-THU)，基于 PyPSA 的中国分省电力系统容量规划模型，使用了本数据。

问题或数据需求：请[提交 issue](https://github.com/ruikelyu/China-Renewable-Profiles/issues)。
