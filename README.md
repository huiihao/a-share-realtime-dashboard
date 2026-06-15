<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Flask-3.0+-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask">
  <img src="https://img.shields.io/badge/A股-5207只-35a86b?style=for-the-badge" alt="Coverage">
  <img src="https://img.shields.io/badge/数据源-4路-58a6ff?style=for-the-badge" alt="Data">
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="License">
</p>

<h1 align="center">📊 A 股实时看盘</h1>
<h3 align="center">5207 只股票 · 4 路数据源 · 8 秒全量刷新 · 双主题界面</h3>
<h4 align="center">量化投资数据基础设施 — 看盘面板是镜子，数据管道才是引擎</h4>

---

## 📖 目录

- [💡 为什么做这个](#-为什么做这个)
- [🚀 快速开始](#-快速开始)
- [🎛️ 面板功能](#️-面板功能)
- [📡 数据管道](#-数据管道)
- [🏗️ 技术架构](#️-技术架构)
- [🔧 API 参考](#-api-参考)
- [📊 量化工作流](#-量化工作流)
- [📁 项目结构](#-项目结构)
- [🤝 贡献](#-贡献)

---

## 💡 为什么做这个

量化投资的第一步永远是 **可靠的数据**。

| 层级 | 说明 |
|------|------|
| 🖥️ **看盘面板** | 可视化验证层 — 确认数据及时、准确 |
| ⚙️ **数据管道** | 多源采集、清洗、存储 — 5207 只 × 日 K 线 |
| 📈 **量化策略** | 因子分析、回测、组合优化 — 这才是终极目标 |

> **Dashboard is the mirror; the data pipeline is the engine.**

看盘面板确认数据 OK → 直接拿 `a_stock_all_kline.csv` → pandas 分析、回测、建模。

---

## 🚀 快速开始

```bash
# 克隆仓库
git clone https://github.com/huiihao/a-share-realtime-dashboard.git
cd a-share-realtime-dashboard

# 安装依赖
pip install -r requirements.txt

# 启动看盘面板
python app.py
```

🌐 浏览器打开 **`http://127.0.0.1:5000`**

---

## 🎛️ 面板功能

### 📐 整体布局

```
┌────────────────────────────────────────────────────────┐
│  📈 指数: 上证 4053 +0.5% │ 深证 15153 +1.3% │ ...      │
├────────────────────────────────────────────────────────┤
│  🏛️ 分段: 沪主板 +1.3% │ 科创板 +3.3% │ 创业板 +2.8% │...  │
├──────────┬──────────┬──────────┬───────────────────────┤
│ 📊 5207  │ 📈 3371↑ │ 🎯 196↑ │ 📉 均 +1.64%         │
│   追踪   │ 📉 1691↓ │ 💥 12↓  │ 💰 26430 亿          │
├──────────┴──────────┼──────────┴───────────────────────┤
│ 📈 涨幅榜 (不含涨停)  │ 🚀 涨停板 (全部 278 只)         │
│ 📉 跌幅榜 (不含跌停)  │ 💥 跌停板 (全部 12 只)          │
├──────────────────────┼────────────────────────────────┤
│ 💰 成交额 TOP-N       │ 🏭 行业板块 (独立刷新)          │
└──────────────────────┴────────────────────────────────┘
```

### 🎮 交互控件

| 🎛️ | 位置 | 选项 |
|-----|------|------|
| 📏 **TOP-N** | 涨跌幅 / 成交额 | 20 · 50 · 100 |
| 📡 **数据源** | 顶部导航 | 新浪财经 · 东方财富 · 同花顺 iFinD |
| ⏱️ **刷新间隔** | 顶部导航 | 3s · 5s · 10s · 30s · 60s |
| 🏭 **板块刷新** | 行业面板 | 5min · 10min · 30min (独立定时器) |
| 🌓 **主题** | 右上角 | Light ↔ Dark (localStorage 持久化) |
| 🔴🟢 **颜色** | 右上角 | 红涨绿跌 ↔ 绿涨红跌 (一键互换) |

### ✨ 设计亮点

| 特性 | 说明 |
|------|------|
| 🚀💥 **涨跌停分离** | 涨停板/跌停板独立面板，涨跌榜自动排除 ≥9.9% 的极限涨跌 |
| ♿ **色盲友好** | 上涨=青绿 `#3fb950`，下跌=暖红 `#f85149`，非传统纯红纯绿 |
| 🧹 **数据清洗** | 自动过滤停牌股(price=0)、退市股(pct=-100%) |
| 🦴 **骨架屏** | 首次加载 shimmer 动画，减少感知等待感 |
| 📱 **响应式** | 1024px / 640px 双断点，平板手机均可使用 |
| 💾 **本地回退** | 东方财富 API 不可用时，自动读取同花顺本地 `industry.ini` 计算行业数据 |

---

## 📡 数据管道

看盘面板只是冰山一角 🌊。下面的采集管道才是量化研究的真正基础：

### 🔬 生产级脚本

| 📜 脚本 | 📡 数据源 | 📦 产出 | ⭐ 可靠性 |
|----------|----------|--------|-----------|
| `fetch_baostock.py` | Baostock | **5207 只全量日 K 线** (9 MB) | ⭐⭐⭐⭐⭐ 无频率限制 |
| `market_analysis_v2.py` | 本地 CSV | 全市场看盘分析报告 | ⭐⭐⭐⭐⭐ 离线运行 |
| `monitor_hexin.py` | 同花顺进程 | 网络连接 / 数据流实时监控 | ⭐⭐⭐⭐ |
| `test_ifind.py` | pywencai | 财务·技术·资金流向全方位查询 | ⭐⭐⭐⭐ |
| `setup_mitmproxy.py` | mitmproxy | HTTP 流量拦截，API 逆向分析 | ⭐⭐⭐ |

### 🔀 数据流向

```
┌─────────────┐
│ 新浪财经 API  │── 实时行情 (5,207 只, ~8s 全量) ──┐
├─────────────┤                                    │
│ 东方财富 API  │── 行业板块 (优先, 网络可达时) ────┼──→ Flask API ──→ 🖥️ 看盘面板
├─────────────┤                                    │
│ 同花顺 iFinD │── 财务因子 (PE/ROE/利润增速) ─────┤
├─────────────┤                                    │
│ Baostock    │── 日 K 线 (全历史, 无限制) ────────┴──→ 💾 CSV 文件 ──→ 📊 pandas 量化
└─────────────┘
```

### 🆚 数据源对比

| 🎯 | 🔵 新浪 | 🟠 东方财富 | 🟣 iFinD | 🟢 Baostock |
|---|---------|------------|---------|------------|
| **实时行情** | ✅ 极快 | ✅ | ✅ | ❌ |
| **日 K 线** | ❌ | ✅ | ✅ | ✅ 最稳定 |
| **财务报表** | ❌ | ✅ | ✅ 最全 | ✅ |
| **技术指标** | ❌ | ❌ | ✅ MACD/KDJ | ❌ |
| **行业分类** | ❌ | ✅ 细分 | ✅ 92行业 | ❌ |
| **频率限制** | 宽松 😊 | 严格 ⚠️ | 中等 | 无 🎉 |
| **并发** | ✅ 4线程 | ⚠️ 易封 IP | ⚠️ | ✅ |

> 💡 **推荐组合**: 新浪(实时看盘) + Baostock(日线采集) + iFinD(财务因子) + 本地 industry.ini(行业分类)

---

## 🏗️ 技术架构

```
┌─────────────────────────────────────────────────────┐
│               🖥️ 看盘面板 (Flask + 原生 HTML/CSS)      │
│  ┌──────────┐  ┌──────────┐  ┌───────────────────┐  │
│  │ 🌐 新浪   │  │ 🟠 东方  │  │ 🟣 同花顺 iFinD   │  │
│  │ (主力)   │  │ (板块)   │  │ (pywencai)       │  │
│  └──────────┘  └──────────┘  └───────────────────┘  │
│  ┌──────────────────────────────────────────────┐   │
│  │         💾 本地回退层 (network-proof)          │   │
│  │  industry.ini → 92 行业 × 5207 股票实时计算     │   │
│  └──────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────┤
│            ⚙️ 数据采集管道 (独立 Python 脚本)          │
│  ┌──────────┐  ┌──────────┐  ┌───────────────────┐  │
│  │ Baostock │  │ akshare  │  │ pywencai          │  │
│  │ 日K线    │  │ 实时行情  │  │ 财务+技术指标      │  │
│  └──────────┘  └──────────┘  └───────────────────┘  │
├─────────────────────────────────────────────────────┤
│            📈 量化策略层 (待建设)                      │
│  因子分析 · 回测框架 · 风险模型 · 组合优化 · 实盘对接   │
└─────────────────────────────────────────────────────┘
```

---

## 🔧 API 参考

所有端点返回 JSON。

| 🛣️ Endpoint | 🔍 Params | 📋 说明 |
|-------------|-----------|--------|
| `GET /api/full_snapshot` | `top` (5-200), `source` (sina/eastmoney/ifind) | 全量行情：指数·分段·涨跌比·涨停跌停·成交额 |
| `GET /api/sectors` | — | 行业板块 (东方财富优先 → 本地同花顺回退) |
| `GET /api/health` | — | 服务状态 + 交易时段检测 |

<details>
<summary>📬 点击展开 Response Schema</summary>

```json
{
  "time": "14:30:00",
  "market_open": true,
  "source": "sina",
  "top_n": 20,
  "indices": [
    {"code": "sh000001", "name": "上证指数", "close": 4053.58, "change_pct": 0.55}
  ],
  "boards": [
    {"name": "科创板", "count": 610, "avg_pct": 3.34}
  ],
  "breadth": {
    "total": 5196, "up": 3371, "down": 1691,
    "limit_up": 196, "limit_down": 12,
    "avg_pct": 1.64, "total_amount": 26430
  },
  "gainers": [
    {"code": "sz301526", "name": "国际复材", "close": 8.88, "change_pct": 9.85}
  ],
  "losers": [
    {"code": "sh688398", "name": "赛特新材", "close": 24.50, "change_pct": -8.92}
  ],
  "limit_ups": [
    {"code": "sz301526", "name": "国际复材", "close": 8.88, "change_pct": 20.01}
  ],
  "limit_downs": [
    {"code": "sz002808", "name": "*ST恒久", "close": 12.30, "change_pct": -10.02}
  ],
  "turnover": [
    {"code": "sz300308", "name": "中际旭创", "close": 1197, "amount": 21066237000}
  ]
}
```
</details>

---

## 📊 量化工作流

看盘面板确认数据 OK ✅，然后进入分析：

```python
import pandas as pd
import numpy as np

# 📥 1. 加载数据
df = pd.read_csv('data/a_stock_all_kline.csv',
                 dtype={'code': str}, parse_dates=['date'])

# 📈 2. 计算日收益率
df['return'] = df.groupby('code')['close'].pct_change()

# 🧬 3. 因子构建 — 5日动量
df['momentum_5d'] = df.groupby('code')['close'].transform(
    lambda x: x.pct_change(5)
)

# 🏷️ 4. 横截面排名
df['rank'] = df.groupby('date')['momentum_5d'].rank(pct=True)

# 📊 5. 分层回测
top_quantile = df[df['rank'] >= 0.8]
daily_return = top_quantile.groupby('date')['return'].mean()
cumulative = (1 + daily_return).cumprod()

# 🎯 6. 评估
sharpe = daily_return.mean() / daily_return.std() * np.sqrt(252)
print(f"📊 Sharpe Ratio: {sharpe:.2f}")
```

---

## 📁 项目结构

```
a-share-realtime-dashboard/
├── 📄 app.py                         # Flask 应用入口
├── 📁 templates/
│   └── 🎨 index.html                 # 单文件前端 (31KB, 零外部依赖)
├── 📄 requirements.txt               # flask, requests, pandas...
├── 📄 run.bat                        # Windows 一键启动
├── 📖 README.md                      # 本文档
└── 📁 ../data/                       # 数据目录 (gitignored)
    ├── 📊 a_stock_all_kline.csv      # 全市场日 K 线 (9 MB)
    └── 📋 a_stock_code_name.csv      # 股票代码表
```

---

## 🤝 贡献

本项目是量化投资的 **数据基础层** 🧱。欢迎贡献：

| 🧩 方向 | 📝 内容 |
|--------|--------|
| 🔌 **数据源** | Wind · Tushare · QUANTAXIS · 聚宽 适配器 |
| ⚔️ **回测** | backtrader · zipline · vnpy 集成 |
| 🧬 **因子库** | 技术因子 · 基本面因子 · 另类数据因子 |
| 🎨 **前端** | WebSocket 推送 · ECharts 可视化 · 移动端优化 |

🤝 Fork → PR，或直接提 Issue 讨论。

---

## ⚠️ 免责声明

本项目仅供 **个人学习与量化研究** 使用，不构成任何投资建议。
数据来源于公开 API，开发者不对数据的准确性、完整性、及时性做任何保证。
历史回测结果不代表未来收益。

---

<p align="center">
  <sub>MIT © <a href="https://github.com/huiihao">huiihao</a> · 如果这个项目对你有帮助，请给一颗 ⭐</sub>
</p>
