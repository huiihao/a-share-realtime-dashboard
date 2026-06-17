"""
同花顺 iFinD 实时看盘面板 - Backend v4
数据源: 新浪财经实时行情
"""
from flask import Flask, jsonify, render_template, request
from flask_caching import Cache
import requests
import pandas as pd
import os, time, traceback
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

app = Flask(__name__)
app.config['CACHE_TYPE'] = 'SimpleCache'
app.config['CACHE_DEFAULT_TIMEOUT'] = 8
# 板块单独缓存，时间更长
app.config['CACHE_SECTORS_TIMEOUT'] = 300  # 5分钟
cache = Cache(app)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
STOCK_LIST_FILE = os.path.join(DATA_DIR, "a_stock_code_name.csv")
SINA_URL = "https://hq.sinajs.cn/list="
SINA_HEADERS = {"User-Agent": "Mozilla/5.0", "Referer": "https://finance.sina.com.cn/"}
BATCH_SIZE = 400
REFRESH_SEC = 10

# Major indices for the ticker bar
INDICES = [
    ("sh000001", "上证指数"),
    ("sz399001", "深证成指"),
    ("sz399006", "创业板指"),
    ("sh000688", "科创50"),
]

_stock_codes_cache = None

def get_stock_codes():
    global _stock_codes_cache
    if _stock_codes_cache:
        return _stock_codes_cache
    if os.path.exists(STOCK_LIST_FILE):
        df = pd.read_csv(STOCK_LIST_FILE, dtype={"code": str})
        codes = []
        for c in df["code"]:
            c_str = str(c).zfill(6)
            if c_str.startswith(('6', '5', '9')):
                codes.append(f"sh{c_str}")
            elif c_str.startswith(('0', '3', '2')):
                codes.append(f"sz{c_str}")
            elif c_str.startswith(('8', '4')):
                codes.append(f"bj{c_str}")
        _stock_codes_cache = codes
        return codes
    return []

def parse_sina_line(line):
    if '=' not in line:
        return None
    code_part, data_part = line.split('=', 1)
    code = code_part.split('_')[-1].strip()
    fields = data_part.strip('";\n ').split(',')
    if len(fields) < 10:
        return None
    try:
        name = fields[0]
        price = float(fields[3]) if len(fields) > 3 and fields[3] else 0
        prev_close = float(fields[2]) if len(fields) > 2 and fields[2] else 0
        change_pct = (price - prev_close) / prev_close * 100 if prev_close > 0 else 0

        # 过滤停牌/退市股 (price=0)
        if price <= 0:
            return None

        return {
            'code': code, 'name': name,
            'open': float(fields[1]) if len(fields) > 1 and fields[1] else 0,
            'prev_close': prev_close,
            'close': price,
            'high': float(fields[4]) if len(fields) > 4 and fields[4] else 0,
            'low': float(fields[5]) if len(fields) > 5 and fields[5] else 0,
            'volume': float(fields[8]) if len(fields) > 8 and fields[8] else 0,
            'amount': float(fields[9]) if len(fields) > 9 and fields[9] else 0,
            'change_pct': round(change_pct, 2),
        }
    except (ValueError, IndexError):
        return None

def fetch_sina_batch(codes_batch):
    url = SINA_URL + ','.join(codes_batch)
    try:
        resp = requests.get(url, headers=SINA_HEADERS, timeout=15)
        resp.encoding = 'gb2312'
        return [p for p in (parse_sina_line(l) for l in resp.text.strip().split('\n')) if p]
    except Exception as e:
        print(f"Sina batch error: {e}")
        return []

def fetch_all_stocks():
    codes = get_stock_codes()
    if not codes:
        return []
    all_results = []
    batches = [codes[i:i+BATCH_SIZE] for i in range(0, len(codes), BATCH_SIZE)]
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(fetch_sina_batch, b): b for b in batches}
        for future in as_completed(futures):
            all_results.extend(future.result())
    return all_results

def fetch_indices():
    """获取主要指数行情
    Sina指数格式与股票相同: fields[0]=名称, [1]=今开, [2]=昨收, [3]=最新价, [4]=最高, [5]=最低
    """
    idx_codes = [c for c, _ in INDICES]
    url = SINA_URL + ','.join(idx_codes)
    try:
        resp = requests.get(url, headers=SINA_HEADERS, timeout=10)
        resp.encoding = 'gb2312'
        results = []
        name_map = dict(INDICES)
        for line in resp.text.splitlines():
            line = line.strip()
            if not line or '=' not in line:
                continue
            code_part, data_part = line.split('=', 1)
            code = code_part.split('_')[-1].strip()
            data_part = data_part.strip().strip('"').strip(';').strip('"')
            fields = data_part.split(',')
            if len(fields) < 6:
                continue
            try:
                price = float(fields[3]) if fields[3] else 0       # 最新价 (不是今开!)
                prev_close = float(fields[2]) if fields[2] else 0  # 昨收
                change_pct = (price - prev_close) / prev_close * 100 if prev_close > 0 else 0
                results.append({
                    'code': code,
                    'name': name_map.get(code, fields[0]),
                    'close': price,
                    'change_pct': round(change_pct, 2),
                })
            except (ValueError, IndexError) as e:
                print(f"Index parse error for {code}: {e}")
        return results
    except Exception as e:
        print(f"Index fetch error: {e}")
        return []

def fetch_sectors():
    """获取行业板块行情 - 东方财富API，带重试，多终端尝试"""
    # 尝试不同的东方财富CDN节点
    hosts = [
        "https://push2.eastmoney.com",
        "https://push2his.eastmoney.com",
        "https://80.push2.eastmoney.com",
        "https://17.push2.eastmoney.com",
    ]
    params = {
        "pn": "1", "pz": "100", "po": "1", "np": "1",
        "ut": "bd1d9ddb04089700cf9ecc5dd0f0b4a1",
        "fltt": "2", "invt": "2", "fid": "f3",
        "fs": "m:90+t:2",  # 东财行业分类
        "fields": "f2,f3,f4,f12,f14",
        "_": str(int(time.time() * 1000))
    }
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
               "Referer": "https://quote.eastmoney.com/"}

    for host in hosts:
        for attempt in range(2):
            try:
                url = f"{host}/api/qt/clist/get"
                resp = requests.get(url, params=params, headers=headers,
                                  timeout=8, proxies={"http": None, "https": None})
                data = resp.json()
                if data.get("data") and data["data"].get("diff"):
                    return [{
                        'name': str(item.get('f14', '')),
                        'change_pct': item.get('f3', 0) or 0,
                    } for item in data["data"]["diff"]]
            except Exception:
                if attempt == 0:
                    time.sleep(1)
    return None

# 同花顺行业代码 → 名称映射（从本地 industry.ini 完整提取，90个行业）
THS_INDUSTRY_NAMES = {
    "881101": "种植业与林业", "881102": "养殖业", "881103": "农产品加工",
    "881105": "煤炭开采加工", "881107": "油气开采及服务", "881108": "化学原料",
    "881109": "化学制品", "881112": "钢铁", "881114": "金属新材料", "881115": "有色金属",
    "881116": "建筑装饰", "881117": "通用设备", "881118": "专用设备",
    "881121": "半导体", "881122": "光学光电子", "881123": "电子制造",
    "881124": "消费电子", "881125": "汽车整车", "881126": "汽车零部件",
    "881128": "白色家电", "881129": "视听器材", "881131": "食品加工制造",
    "881132": "饮料制造", "881133": "白酒", "881134": "纺织制造", "881135": "服装家纺",
    "881136": "造纸", "881137": "包装印刷", "881138": "家用轻工", "881139": "化学制药",
    "881140": "中药", "881141": "生物制品", "881142": "医药商业",
    "881143": "医疗器械", "881144": "电力", "881145": "燃气", "881146": "港口航运",
    "881148": "公路铁路运输", "881149": "机场航运", "881150": "物流",
    "881151": "房地产开发", "881152": "银行", "881153": "保险及其他",
    "881155": "证券", "881156": "零售", "881157": "贸易", "881158": "旅游及酒店",
    "881160": "传媒", "881162": "通信服务", "881164": "计算机应用",
    "881165": "综合", "881166": "建筑材料", "881167": "非金属材料",
    "881168": "工业金属", "881169": "贵金属", "881170": "小金属",
    "881171": "自动化设备", "881172": "电子化学品", "881174": "其他电子",
    "881175": "医疗服务", "881177": "其他社会服务", "881178": "环保",
    "881179": "美容护理", "881180": "石油加工贸易", "881181": "教育",
    "881263": "农业服务", "881264": "化学纤维", "881265": "橡胶制品",
    "881266": "塑料制品", "881267": "能源金属", "881268": "工程机械",
    "881269": "轨交设备", "881270": "元件", "881271": "IT服务",
    "881272": "软件开发", "881273": "白酒", "881274": "影视院线",
    "881275": "游戏", "881276": "互联网电商", "881277": "军工",
    "881278": "光伏设备", "881279": "风电设备", "881280": "电池",
    "881281": "电网", "881282": "新能源设备", "881283": "多元金融",
    "881284": "军工电子",
}

def load_industry_mapping():
    """从同花顺本地 industry.ini 加载行业→股票映射"""
    # 优先环境变量，否则使用默认安装路径
    ini_path = os.environ.get(
        "HEXIN_INDUSTRY_PATH",
        os.path.join(os.environ.get("ProgramFiles", "C:/Program Files"),
                     "同花顺软件/同花顺/industry.ini")
    )
    # 也检查常见安装位置
    if not os.path.exists(ini_path):
        alt_paths = [
            r"D:\同花顺软件\同花顺\industry.ini",
            r"C:\同花顺软件\同花顺\industry.ini",
            os.path.join(os.path.dirname(__file__), "industry.ini"),
        ]
        for alt in alt_paths:
            if os.path.exists(alt):
                ini_path = alt
                break
    if not os.path.exists(ini_path):
        return {}
    mapping = {}
    with open(ini_path, "r", encoding="gbk", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or '=' not in line or line.startswith('['):
                continue
            code, stocks = line.split('=', 1)
            # 跳过名称行（以;结尾）和未知行业
            if stocks.endswith(';') or code not in THS_INDUSTRY_NAMES:
                continue
            mapping[code] = [s.strip() for s in stocks.split(',') if s.strip()]
    return mapping

def compute_industry_performance(rows):
    """从实时股票数据 + 本地行业分类计算行业表现"""
    industry_map = load_industry_mapping()
    if not industry_map:
        return []

    # 构建代码→涨跌幅的查找表（新浪格式 sh600xxx vs 同花顺格式 600xxx）
    price_map = {}
    for r in rows:
        code = r['code'].replace('sh', '').replace('sz', '').replace('bj', '')
        price_map[code] = r['change_pct']

    results = []
    for ind_code, stock_list in industry_map.items():
        pcts = [price_map[s] for s in stock_list if s in price_map]
        if len(pcts) >= 3:  # 至少3只股票有数据
            avg_pct = sum(pcts) / len(pcts)
            results.append({
                'name': THS_INDUSTRY_NAMES.get(ind_code, ind_code),
                'change_pct': round(avg_pct, 2),
            })

    results.sort(key=lambda x: x['change_pct'], reverse=True)
    return results  # 返回全部行业（面板可滚动查看）

def is_market_open():
    now = datetime.now()
    if now.weekday() >= 5:
        return False
    t = now.strftime('%H%M')
    return ('0930' <= t <= '1130') or ('1300' <= t <= '1500')

# ============ API Endpoints ============

@app.route('/')
def index():
    return render_template('index.html', refresh_sec=REFRESH_SEC)

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'ok',
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'market_open': is_market_open(),
        'source': 'sina'
    })

@app.route('/api/full_snapshot')
@cache.cached(timeout=8, query_string=True)
def full_snapshot():
    """全量快照 - 股票行情 (不含板块)"""
    top_n = request.args.get('top', 20, type=int)
    top_n = max(5, min(200, top_n))  # 限制范围 5-200

    source = request.args.get('source', 'sina')

    result = {
        'time': datetime.now().strftime('%H:%M:%S'),
        'market_open': is_market_open(),
        'indices': [],
        'boards': [],
        'breadth': {},
        'gainers': [],
        'losers': [],
        'limit_ups': [],
        'limit_downs': [],
        'turnover': [],
        'source': source,
        'top_n': top_n,
    }

    start = time.time()
    result['indices'] = fetch_indices()

    rows = []
    try:
        rows = fetch_all_stocks()
    except Exception as e:
        print(f"Fetch error: {e}")

    if rows:
        valid = [r for r in rows if -99 < (r['change_pct'] or 0) < 99]
        changes = [r['change_pct'] for r in valid]
        amounts = [r['amount'] for r in valid if r.get('amount', 0) > 0]
        total_amt = sum(amounts)

        # 分离涨停/跌停股
        limit_up_stocks = sorted(
            [r for r in valid if (r['change_pct'] or 0) >= 9.9],
            key=lambda x: x['change_pct'] or 0, reverse=True
        )
        limit_down_stocks = sorted(
            [r for r in valid if (r['change_pct'] or 0) <= -9.9],
            key=lambda x: x['change_pct'] or 0
        )

        # 普通涨跌榜（排除涨停跌停股）
        normal = [r for r in valid if -9.9 < (r['change_pct'] or 0) < 9.9]

        result['breadth'] = {
            'total': len(valid),
            'up': sum(1 for c in changes if c > 0),
            'down': sum(1 for c in changes if c < 0),
            'flat': sum(1 for c in changes if c == 0),
            'limit_up': len(limit_up_stocks),
            'limit_down': len(limit_down_stocks),
            'avg_pct': round(sum(changes) / len(changes), 2) if changes else 0,
            'median_pct': round(sorted(changes)[len(changes)//2], 2) if changes else 0,
            'total_amount': round(total_amt / 1e8, 0),
        }

        result['limit_ups'] = limit_up_stocks  # 全部涨停
        result['limit_downs'] = limit_down_stocks  # 全部跌停
        result['gainers'] = sorted(normal, key=lambda x: x['change_pct'] or 0, reverse=True)[:top_n]
        result['losers'] = sorted(normal, key=lambda x: x['change_pct'] or 0)[:top_n]
        result['turnover'] = sorted(valid, key=lambda x: x.get('amount', 0) or 0, reverse=True)[:top_n]

        # 市场分段 (沪市主板/创业板/科创板等)
        boards_def = [
            ('沪市主板', lambda c: c.startswith('sh60')),
            ('科创板',   lambda c: c.startswith('sh68')),
            ('深市主板', lambda c: c.startswith('sz000') or c.startswith('sz001')),
            ('中小板',   lambda c: c.startswith('sz002')),
            ('创业板',   lambda c: c.startswith('sz30')),
            ('北交所',   lambda c: c.startswith('bj')),
        ]
        result['boards'] = []
        for bname, pred in boards_def:
            group = [r for r in valid if pred(r['code'])]
            if group:
                avg_pct = sum(r['change_pct'] for r in group) / len(group)
                result['boards'].append({
                    'name': bname, 'count': len(group),
                    'avg_pct': round(avg_pct, 2),
                })

    elapsed = time.time() - start
    print(f"Snapshot: {len(rows)} stocks in {elapsed:.1f}s (top_n={top_n})")

    return jsonify(result)

@app.route('/api/sectors')
def sectors():
    """行业板块 - 优先本地同花顺92行业(白酒/银行/医药等)，东方财富作为备选"""
    force = request.args.get('force', '0') == '1'

    # ① 本地同花顺 industry.ini — 92个传统大行业（含白酒/银行/房地产/医药等）
    rows = fetch_all_stocks()
    if rows:
        valid = [r for r in rows if -99 < (r['change_pct'] or 0) < 99]
        local_sectors = compute_industry_performance(valid)
        if local_sectors:
            # 异步尝试东方财富，但不阻塞返回
            return jsonify({'time': datetime.now().strftime('%H:%M:%S'), 'sectors': local_sectors, 'source': 'local'})

    # ② 回退：东方财富API
    em_data = fetch_sectors()
    if em_data:
        return jsonify({'time': datetime.now().strftime('%H:%M:%S'), 'sectors': em_data, 'source': 'eastmoney'})

    return jsonify({'time': datetime.now().strftime('%H:%M:%S'), 'sectors': [], 'source': 'unavailable'})

@app.route('/api/board_performance')
def board_performance():
    """市场分段表现 - 从已加载的股票数据计算，无外部依赖"""
    rows = fetch_all_stocks()
    if not rows:
        return jsonify({'boards': []})

    valid = [r for r in rows if -99 < (r['change_pct'] or 0) < 99]

    boards_def = [
        ('沪市主板', lambda c: c.startswith('sh60')),
        ('深市主板', lambda c: c.startswith('sz0') and not c.startswith('sz00')),
        ('创业板',   lambda c: c.startswith('sz30')),
        ('科创板',   lambda c: c.startswith('sh68')),
        ('中小板',   lambda c: c.startswith('sz00')),
        ('北交所',   lambda c: c.startswith('bj')),
    ]

    boards = []
    for name, pred in boards_def:
        group = [r for r in valid if pred(r['code'])]
        if group:
            avg_pct = sum(r['change_pct'] for r in group) / len(group)
            up = sum(1 for r in group if r['change_pct'] > 0)
            down = sum(1 for r in group if r['change_pct'] < 0)
            boards.append({
                'name': name,
                'count': len(group),
                'avg_pct': round(avg_pct, 2),
                'up': up,
                'down': down,
            })

    boards.sort(key=lambda x: x['avg_pct'], reverse=True)
    return jsonify({'boards': boards, 'time': datetime.now().strftime('%H:%M:%S')})


if __name__ == '__main__':
    print("=" * 50)
    print("  A股实时看盘面板 v4")
    print("  http://127.0.0.1:5000")
    print("=" * 50)
    print(f"  主数据源: 新浪财经实时行情")
    print(f"  板块数据: 东方财富")
    print(f"  刷新间隔: {REFRESH_SEC}秒")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
