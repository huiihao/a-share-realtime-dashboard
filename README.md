<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Flask-3.0+-000000?style=flat&logo=flask&logoColor=white" alt="Flask">
  <img src="https://img.shields.io/badge/Coverage-5207%20A%20Shares-35a86b?style=flat" alt="Coverage">
  <img src="https://img.shields.io/badge/Data%20Sources-4-58a6ff?style=flat" alt="Data Sources">
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=flat" alt="License">
</p>

<h1 align="center">A-Share Real-Time Dashboard</h1>
<h3 align="center">A股实时看盘 · 量化数据基础设施</h3>

<p align="center">
  <strong>5207 只 A 股 · 4 路数据源 · 10 秒全量刷新 · 双主题 Bloomberg 风格界面</strong>
</p>

---

## Why This Exists

量化投资的第一步永远是**可靠的数据**。这个项目的核心是一套多源数据采集管道，能够稳定地获取全市场 A 股行情——看盘面板只是数据质量的**可视化验证层**。

> **Dashboard is the mirror; the data pipeline is the engine.**

你可以把看盘面板当作确认"数据是对的、及时的"的眼睛，然后直接拿 `data/a_stock_all_kline.csv`（5207 只 × 日 K 线）去做 pandas 因子分析、策略回测、统计建模。

---

## Quick Start

```bash
git clone https://github.com/huiihao/a-share-realtime-dashboard.git
cd a-share-realtime-dashboard
pip install -r requirements.txt
python app.py
```

浏览器打开 `http://127.0.0.1:5000`

---

## Dashboard Features

### Panel Layout

```
┌──────────────────────────────────────────────────────┐
│  🔵 上证 4053  +0.55%  │  🟢 深证 15153  +1.27%     │
│  🟢 创业板 3896 +1.72% │  🟢 科创50 1687  +1.47%    │
├──────────┬───────────┬───────────┬───────────────────┤
│ 5207 只  │ 3371↑/1691↓│ 196涨停/12跌停│ 均+1.64% / 26430亿│
├──────────────┼──────────────┼──────────────┼──────────────┤
│ 📈 涨幅榜     │ 📉 跌幅榜     │ 🚀 涨停板     │ 💥 跌停板    │
│ (不含涨停)    │ (不含跌停)    │ (全部)       │ (全部)       │
├──────────────┴──────────────┼──────────────┴──────────────┤
│ 💰 成交额 TOP-N (独立选择)    │ 🏭 行业板块 (5/10/30分钟刷新) │
└─────────────────────────────┴─────────────────────────────┘
```

### Interactive Controls

| 控件 | 位置 | 功能 |
|------|------|------|
| **TOP-N 选择器** | 涨幅榜/成交额面板 | 20 / 50 / 100 可调，涨跌榜联动、成交额独立 |
| **数据源切换** | 顶部导航栏 | 新浪财经 / 东方财富 / 同花顺 iFinD |
| **板块刷新间隔** | 行业板块面板 | 5 / 10 / 30 分钟独立定时器 |
| **Light/Dark 主题** | 顶部导航栏 | localStorage 持久化，刷新不丢失 |

### Design Highlights

- **涨停/跌停独立展示** — 涨幅榜自动排除 ≥9.9% 的涨停股，避免涨停板淹没真实涨幅排行
- **色盲友好配色** — 上涨用青绿 (`#3fb950`)，下跌用暖红 (`#f85149`)，非传统纯红/纯绿
- **数据质量过滤** — 自动排除停牌股（price=0）、退市股（pct=-100%）
- **骨架屏加载** — 首次加载时 shimmer 动画，减少感知等待
- **响应式布局** — 1024px / 640px 两个断点，平板和手机均可使用

---

## Data Pipeline

看盘面板是冰山一角。真正的核心是下面的数据采集管道：

### Production-Ready Scripts

| 脚本 | 数据源 | 产出 | 可靠性 |
|------|--------|------|--------|
| `fetch_baostock.py` | Baostock | **5207 只全量日 K 线** (9 MB CSV) | ⭐⭐⭐⭐⭐ 无频率限制 |
| `market_analysis_v2.py` | 本地 CSV | 全市场看盘分析报告 | ⭐⭐⭐⭐⭐ 离线运行 |
| `monitor_hexin.py` | 同花顺进程 | 网络连接/数据流实时监控 | ⭐⭐⭐⭐ |
| `test_ifind.py` | pywencai/iFinD | 财务/技术/资金流向全方位查询 | ⭐⭐⭐⭐ |
| `setup_mitmproxy.py` | mitmproxy | HTTP 流量拦截，逆向 API | ⭐⭐⭐ |

### Data Flow

```
新浪财经 (实时行情) ──┐
东方财富 (板块/历史) ──┼──→ Flask API ──→ 看盘面板 (浏览器)
同花顺 iFinD (财务)  ──┤
Baostock (日K线)    ──┴──→ CSV 文件 ──→ pandas 量化分析
```

### Data Source Comparison

| | 新浪 | 东方财富 | iFinD | Baostock |
|---|---|---|---|---|
| **实时行情** | ✅ 极快 | ✅ | ✅ | ❌ |
| **日 K 线** | ❌ | ✅ | ✅ | ✅ 最稳定 |
| **财务数据** | ❌ | ✅ | ✅ 最全 | ✅ |
| **技术指标** | ❌ | ❌ | ✅ | ❌ |
| **频率限制** | 宽松 | 严格 ⚠️ | 中等 | 无 |
| **并发** | ✅ | ⚠️ 易封 IP | ⚠️ | ✅ |

> **推荐组合**: 新浪（实时看盘）+ Baostock（日线采集）+ iFinD（财务因子）

---

## API Reference

所有端点返回 JSON，支持 CORS。

| Endpoint | Params | Description |
|----------|--------|-------------|
| `GET /api/full_snapshot` | `top` (5-200), `source` (sina/eastmoney/ifind) | 全量行情快照：指数、涨跌比、涨跌榜、涨停板、成交额 |
| `GET /api/sectors` | - | 行业板块行情（独立缓存 5 分钟） |
| `GET /api/health` | - | 服务状态 + 交易时段检测 |

**Response schema** (`/api/full_snapshot`):

```json
{
  "time": "14:30:00",
  "market_open": true,
  "source": "sina",
  "top_n": 20,
  "indices": [{"code":"sh000001","name":"上证指数","close":4053.58,"change_pct":0.55}],
  "breadth": {"total":5196,"up":3371,"down":1691,"limit_up":196,"limit_down":12,"avg_pct":1.64,"total_amount":26430},
  "gainers": [{"code":"sz301526","name":"国际复材","close":8.88,"change_pct":9.85}],
  "losers": [{"code":"sh688398","name":"赛特新材","close":24.50,"change_pct":-8.92}],
  "limit_ups": [{"code":"sz301526","name":"国际复材","close":8.88,"change_pct":20.01}],
  "limit_downs": [{"code":"sz002808","name":"*ST恒久","close":12.30,"change_pct":-10.02}],
  "turnover": [{"code":"sz300308","name":"中际旭创","close":1197,"change_pct":4.17,"amount":21066237000}]
}
```

---

## Quant Workflow

这是项目的真正使用方式——看盘面板确认数据 OK，然后进入分析：

```python
import pandas as pd
import numpy as np

# 1. 加载数据
df = pd.read_csv('data/a_stock_all_kline.csv', dtype={'code': str}, parse_dates=['date'])

# 2. 计算日收益率
df['return'] = df.groupby('code')['close'].pct_change()

# 3. 因子构建：过去 5 日动量
df['momentum_5d'] = df.groupby('code')['close'].transform(
    lambda x: x.pct_change(5)
)

# 4. 横截面排名
df['rank'] = df.groupby('date')['momentum_5d'].rank(pct=True)

# 5. 分层回测
top_quantile = df[df['rank'] >= 0.8]
daily_return = top_quantile.groupby('date')['return'].mean()
cumulative = (1 + daily_return).cumprod()

print(f"Sharpe Ratio: {daily_return.mean() / daily_return.std() * np.sqrt(252):.2f}")
```

---

## Project Structure

```
a-share-realtime-dashboard/
├── app.py                         # Flask 应用入口
├── templates/index.html           # 单文件前端 (31KB, 零外部依赖)
├── requirements.txt               # flask, flask-caching, pandas, requests
├── run.bat                        # Windows 一键启动
├── README.md                      # 本文档
└── ../data/                       # 数据目录 (gitignored)
    ├── a_stock_all_kline.csv      # 全市场日K线
    └── a_stock_code_name.csv      # 股票代码表
```

---

## Contributing

本项目是量化投资的**数据基础层**。欢迎贡献：

- 新的数据源适配器（Wind、Tushare、QUANTAXIS 等）
- 策略回测框架集成（backtrader、zipline、vnpy）
- 因子库建设与验证
- 前端增强（WebSocket 推送、更多可视化图表）

Fork → PR，或者直接提 Issue 讨论。

---

## Disclaimer

本项目仅供个人学习与量化研究使用，不构成任何投资建议。数据来源于公开 API，开发者不对数据的准确性、完整性、及时性做任何保证。使用本项目的回测结果不代表未来收益。

---

## License

MIT © [huiihao](https://github.com/huiihao)
