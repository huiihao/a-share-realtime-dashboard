# A股实时看盘 & 量化数据平台

基于多数据源的 A 股实时行情仪表板 + 全市场量化数据采集管道。

> **核心定位**: 量化投资数据基础设施。看盘面板用于直观验证数据的及时性与可靠性，实际价值在于支撑代码化的量化策略研究与统计分析。

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ 功能

### 📊 实时看盘面板

| 模块 | 说明 |
|------|------|
| **指数行情** | 上证/深证/创业板/科创50 实时报价 |
| **市场概览** | 涨跌比、涨停跌停数、平均涨跌、总成交额 |
| **涨幅榜** | TOP N（20/50/100），**自动排除涨停股** |
| **跌幅榜** | TOP N（20/50/100），**自动排除跌停股** |
| **涨停板** | 独立展示所有涨停股票（≥9.9%） |
| **跌停板** | 独立展示所有跌停股票（≤-9.9%） |
| **成交额** | TOP N 成交额排行 |
| **行业板块** | 柱状图可视化 + **独立刷新周期**（5/10/30分钟） |
| **主题切换** | Light/Dark 双主题，localStorage 持久化 |
| **数据源选择** | 新浪财经 / 东方财富 / 同花顺 iFinD 可切换 |

### 📡 数据采集管道

| 模块 | 数据源 | 覆盖 | 状态 |
|------|--------|------|------|
| `fetch_baostock.py` | Baostock | 5,207 只 A 股日 K 线 | ✅ |
| `fetch_kline_fast.py` | 东方财富 | 批量日 K 线（多线程） | ⚠️ 易限流 |
| `market_analysis_v2.py` | 本地数据 | 全市场看盘分析报告 | ✅ |
| `monitor_hexin.py` | 同花顺进程 | 网络连接/数据流监控 | ✅ |
| `test_ifind.py` | pywencai | iFinD 数据库全面测试 | ✅ |
| `setup_mitmproxy.py` | mitmproxy | HTTP 流量拦截 | ✅ |

## 🚀 快速开始

### 安装

```bash
git clone <repo-url>
cd realtime_dashboard
pip install -r requirements.txt
```

### 启动看盘面板

```bash
python app.py
# 浏览器打开 http://127.0.0.1:5000
```

### 数据采集

```bash
# 全市场日K线（推荐 - 稳定可靠）
python ../fetch_baostock.py

# 市场分析报告
python ../market_analysis_v2.py

# 同花顺进程监控
python ../monitor_hexin.py
```

## 📡 数据源对比

| 特性 | 新浪财经 | 东方财富 | 同花顺 iFinD | Baostock |
|------|---------|---------|-------------|----------|
| **实时性** | ✅ 实时 | ✅ 实时 | ✅ 实时 | ❌ 日线 |
| **稳定性** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **频率限制** | 宽松 | 严格 | 中等 | 无 |
| **财务数据** | ❌ | ✅ | ✅ | ✅ |
| **技术指标** | ❌ | ❌ | ✅ | ❌ |
| **数据格式** | 简单文本 | JSON | DataFrame | DataFrame |
| **并发支持** | ✅ | ⚠️ | ⚠️ | ✅ |
| **免费** | ✅ | ✅ | ✅ | ✅ |

## 🏗️ 技术架构

```
┌─────────────────────────────────────────────────┐
│                  看盘面板 (Flask)                  │
│  ┌──────────┐  ┌──────────┐  ┌───────────────┐  │
│  │ 新浪 API  │  │ 东方财富  │  │ 同花顺 iFinD  │  │
│  │ (主力)   │  │ (板块)   │  │ (pywencai)   │  │
│  └──────────┘  └──────────┘  └───────────────┘  │
├─────────────────────────────────────────────────┤
│              数据采集管道 (Python)                 │
│  ┌──────────┐  ┌──────────┐  ┌───────────────┐  │
│  │ Baostock │  │ akshare  │  │ pywencai      │  │
│  │ 日K线    │  │ 实时行情  │  │ 财务+指标     │  │
│  └──────────┘  └──────────┘  └───────────────┘  │
├─────────────────────────────────────────────────┤
│              量化策略层 (待开发)                    │
│  因子分析 · 回测框架 · 风险模型 · 组合优化          │
└─────────────────────────────────────────────────┘
```

## 📁 项目结构

```
tonghuashun/
├── realtime_dashboard/        # 实时看盘面板
│   ├── app.py                 # Flask 后端
│   ├── templates/index.html   # 前端界面
│   ├── requirements.txt       # Python 依赖
│   ├── run.bat                # Windows 启动脚本
│   └── README.md              # 本文档
├── data/                      # 数据存储
│   ├── a_stock_all_kline.csv  # 全市场日K线 (9 MB)
│   ├── a_stock_code_name.csv  # 股票代码表
│   └── market_report_full.csv # 市场分析报告
├── fetch_baostock.py          # Baostock 数据采集
├── fetch_kline_fast.py        # 东方财富批量采集
├── market_analysis_v2.py      # 市场分析
├── monitor_hexin.py           # 同花顺监控
├── test_ifind.py              # iFinD 数据库测试
└── setup_mitmproxy.py         # mitmproxy 配置
```

## 🔧 API 端点

| 端点 | 方法 | 说明 | 参数 |
|------|------|------|------|
| `/` | GET | 看板主页 | - |
| `/api/full_snapshot` | GET | 全量行情 | `top`(N), `source`(sina/eastmoney/ifind) |
| `/api/sectors` | GET | 行业板块 | 独立缓存5分钟 |
| `/api/health` | GET | 健康检查 | - |

## 📊 数据使用示例

```python
import pandas as pd

# 加载全市场日K线
df = pd.read_csv('data/a_stock_all_kline.csv', dtype={'code': str})

# 计算每只股票的月收益率
df['date'] = pd.to_datetime(df['date'])
monthly_return = df.groupby('code').apply(
    lambda x: (x['close'].iloc[-1] / x['close'].iloc[0] - 1) * 100
)

# 筛选强势股
strong = monthly_return[monthly_return > 20]
print(f"月涨幅>20%的股票: {len(strong)} 只")
```

## ⚠️ 注意事项

- 免费 API 均有频率限制，建议刷新间隔 ≥ 5 秒
- 同花顺 iFinD 需安装客户端才能使用完整功能（pywencai 通过 Web API 间接访问）
- 本项目的看盘面板为数据验证工具，量化策略开发推荐直接使用数据文件
- 仅供个人学习与研究使用，不构成投资建议

## 📄 许可

MIT License
