#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lunar-weather: 获取天气数据（Open-Meteo，无需 API key）
用法: python3 get_weather_data.py <城市> [YYYY-MM-DD| today| tomorrow]
"""
import socket, sys, json, urllib.request, urllib.error, ssl, time
from datetime import datetime, date, timedelta

CITY_COORDS = {
    '北京': (39.9042, 116.4074),
    '上海': (31.2304, 121.4737), '南京': (32.0603, 118.7969),
    '杭州': (30.2741, 120.1551), '苏州': (31.2989, 120.5853),
    '无锡': (31.4912, 120.3119),
    '广州': (23.1291, 113.2644), '深圳': (22.5431, 114.0579),
    '成都': (30.5728, 104.0668), '武汉': (30.5928, 114.3055),
    '西安': (34.3416, 108.9398), '重庆': (29.4316, 106.9123),
    '东京': (35.6762, 139.6503), '香港': (22.3193, 114.1694),
}

CITY_ALIASES = {
    '北京市': '北京', '上海市': '上海', '南京市': '南京',
    '杭州市': '杭州', '苏州市': '苏州', '无锡市': '无锡',
    '广州市': '广州', '深圳市': '深圳', '成都市': '成都', '武汉市': '武汉',
    '西安市': '西安', '重庆市': '重庆', '东京都': '东京',
}

MAX_FORECAST_DAYS = 16

WEATHER_CODES = {
    0: ('☀️', '晴'), 1: ('🌤️', '晴间多云'), 2: ('⛅', '多云'), 3: ('☁️', '阴'),
    45: ('🌫️', '雾'), 48: ('🌫️', '霜雾'),
    51: ('🌦️', '小毛毛雨'), 53: ('🌦️', '中毛毛雨'), 55: ('🌧️', '大毛毛雨'),
    61: ('🌧️', '小雨'), 63: ('🌧️', '中雨'), 65: ('🌧️', '大雨'),
    71: ('🌨️', '小雪'), 73: ('🌨️', '中雪'), 75: ('❄️', '大雪'),
    80: ('🌦️', '阵雨'), 81: ('🌧️', '中阵雨'), 82: ('⛈️', '大阵雨'),
    85: ('🌨️', '阵雪'), 86: ('❄️', '大阵雪'),
    95: ('⛈️', '雷暴'), 96: ('⛈️', '雷暴+小冰雹'), 99: ('⛈️', '雷暴+大冰雹'),
}

W_CODE_NIGHT = {0: '🌙', 1: '🌙', 2: '☁️', 3: '☁️'}

WIND_LEVELS = [(5,'微风',' breeze'), (15,'轻风',' light breeze'), (25,'和风',' moderate breeze'), (40,'强风',' strong breeze'), (60,'大风',' strong wind')]

UV_LEVELS = [(2,'弱','无需防护'), (5,'中等','涂防晒'), (8,'强','涂防晒+遮阳'), (11,'极强','避免外出')]

# 1900-2100 农历数据；用于无外部依赖地生成每日农历提示。
LUNAR_INFO = [
    0x04bd8,0x04ae0,0x0a570,0x054d5,0x0d260,0x0d950,0x16554,0x056a0,0x09ad0,0x055d2,
    0x04ae0,0x0a5b6,0x0a4d0,0x0d250,0x1d255,0x0b540,0x0d6a0,0x0ada2,0x095b0,0x14977,
    0x04970,0x0a4b0,0x0b4b5,0x06a50,0x06d40,0x1ab54,0x02b60,0x09570,0x052f2,0x04970,
    0x06566,0x0d4a0,0x0ea50,0x06e95,0x05ad0,0x02b60,0x186e3,0x092e0,0x1c8d7,0x0c950,
    0x0d4a0,0x1d8a6,0x0b550,0x056a0,0x1a5b4,0x025d0,0x092d0,0x0d2b2,0x0a950,0x0b557,
    0x06ca0,0x0b550,0x15355,0x04da0,0x0a5d0,0x14573,0x052d0,0x0a9a8,0x0e950,0x06aa0,
    0x0aea6,0x0ab50,0x04b60,0x0aae4,0x0a570,0x05260,0x0f263,0x0d950,0x05b57,0x056a0,
    0x096d0,0x04dd5,0x04ad0,0x0a4d0,0x0d4d4,0x0d250,0x0d558,0x0b540,0x0b6a0,0x195a6,
    0x095b0,0x049b0,0x0a974,0x0a4b0,0x0b27a,0x06a50,0x06d40,0x0af46,0x0ab60,0x09570,
    0x04af5,0x04970,0x064b0,0x074a3,0x0ea50,0x06b58,0x055c0,0x0ab60,0x096d5,0x092e0,
    0x0c960,0x0d954,0x0d4a0,0x0da50,0x07552,0x056a0,0x0abb7,0x025d0,0x092d0,0x0cab5,
    0x0a950,0x0b4a0,0x0baa4,0x0ad50,0x055d9,0x04ba0,0x0a5b0,0x15176,0x052b0,0x0a930,
    0x07954,0x06aa0,0x0ad50,0x05b52,0x04b60,0x0a6e6,0x0a4e0,0x0d260,0x0ea65,0x0d530,
    0x05aa0,0x076a3,0x096d0,0x04bd7,0x04ad0,0x0a4d0,0x1d0b6,0x0d250,0x0d520,0x0dd45,
    0x0b5a0,0x056d0,0x055b2,0x049b0,0x0a577,0x0a4b0,0x0aa50,0x1b255,0x06d20,0x0ada0,
    0x14b63,0x09370,0x049f8,0x04970,0x064b0,0x168a6,0x0ea50,0x06b20,0x1a6c4,0x0aae0,
    0x0a2e0,0x0d2e3,0x0c960,0x0d557,0x0d4a0,0x0da50,0x05d55,0x056a0,0x0a6d0,0x055d4,
    0x052d0,0x0a9b8,0x0a950,0x0b4a0,0x0b6a6,0x0ad50,0x055a0,0x0aba4,0x0a5b0,0x052b0,
    0x0b273,0x06930,0x07337,0x06aa0,0x0ad50,0x14b55,0x04b60,0x0a570,0x054e4,0x0d160,
    0x0e968,0x0d520,0x0daa0,0x16aa6,0x056d0,0x04ae0,0x0a9d4,0x0a2d0,0x0d150,0x0f252,
    0x0d520,
]
LUNAR_MONTHS = '正二三四五六七八九十冬腊'
LUNAR_DAYS = ['初一','初二','初三','初四','初五','初六','初七','初八','初九','初十','十一','十二','十三','十四','十五','十六','十七','十八','十九','二十','廿一','廿二','廿三','廿四','廿五','廿六','廿七','廿八','廿九','三十']
LUNAR_FESTIVALS = {(1,1):'春节',(1,15):'元宵',(2,2):'龙抬头',(5,5):'端午',(7,7):'七夕',(8,15):'中秋',(9,9):'重阳',(12,8):'腊八',(12,23):'小年'}
SOLAR_TERMS = {(1,5):'小寒',(1,20):'大寒',(2,4):'立春',(2,19):'雨水',(3,5):'惊蛰',(3,20):'春分',(4,4):'清明',(4,20):'谷雨',(5,5):'立夏',(5,21):'小满',(6,6):'芒种',(6,21):'夏至',(7,7):'小暑',(7,23):'大暑',(8,7):'立秋',(8,23):'处暑',(9,7):'白露',(9,23):'秋分',(10,8):'寒露',(10,23):'霜降',(11,7):'立冬',(11,22):'小雪',(12,7):'大雪',(12,22):'冬至'}
GAN = '甲乙丙丁戊己庚辛壬癸'
ZHI = '子丑寅卯辰巳午未申酉戌亥'
BAGUA = [
    ('乾', '天', '健行、决断、开局'), ('兑', '泽', '沟通、成交、表达'),
    ('离', '火', '看清、曝光、创作'), ('震', '雷', '启动、突破、行动'),
    ('巽', '风', '渗透、传播、调整'), ('坎', '水', '谨慎、复盘、避险'),
    ('艮', '山', '止损、沉淀、边界'), ('坤', '地', '承载、整理、蓄力'),
]
WEST_SIGNS = [
    ((1,20),'水瓶'), ((2,19),'双鱼'), ((3,21),'白羊'), ((4,20),'金牛'),
    ((5,21),'双子'), ((6,22),'巨蟹'), ((7,23),'狮子'), ((8,23),'处女'),
    ((9,23),'天秤'), ((10,24),'天蝎'), ((11,22),'射手'), ((12,22),'摩羯'), ((12,32),'水瓶')
]

def aqi_label(v):
    if v is None: return '—', '良'
    if v<=50: return '✅ 优','优'
    if v<=100: return '🟡 良','良'
    if v<=150: return '🟠 轻度','轻度污染'
    if v<=200: return '🔴 中度','中度污染'
    if v<=300: return '🟣 重度','重度污染'
    return '⚫ 严重','严重污染'

def get_alert(code, precip=0):
    if code in (95,96,99): return '🔴 红色预警｜极端天气，建议非必要不出门'
    if code in (65,67,73,75,86): return '🟠 橙色预警｜强降水/强降雪，外出注意安全'
    if code in (61,63,71,80,81,85) or precip>60: return '🟡 黄色预警｜雨雪天气，带伞防滑'
    if code in (45,48): return '🟡 黄色预警｜有雾，能见度低，减速慢行'
    return '✅ 今日暂无明显异常天气'

def wind_desc(speed):
    for thresh, label, _ in WIND_LEVELS:
        if speed <= thresh: return label
    return '狂风'

def leap_month(y): return LUNAR_INFO[y-1900] & 0xf
def leap_days(y): return 30 if leap_month(y) and (LUNAR_INFO[y-1900] & 0x10000) else (29 if leap_month(y) else 0)
def month_days(y, m): return 30 if (LUNAR_INFO[y-1900] & (0x10000 >> m)) else 29
def lunar_year_days(y): return 348 + sum(1 for i in (0x8000,0x4000,0x2000,0x1000,0x0800,0x0400,0x0200,0x0100,0x0080,0x0040,0x0020,0x0010) if LUNAR_INFO[y-1900] & i) + leap_days(y)

def lunar_info_for(ymd):
    d = datetime.strptime(ymd, '%Y-%m-%d').date()
    offset = (d - date(1900,1,31)).days
    y = 1900
    while y < 2101 and offset >= lunar_year_days(y):
        offset -= lunar_year_days(y)
        y += 1

    lm = leap_month(y)
    is_leap = False
    m = 1
    while m <= 12:
        md = month_days(y, m)
        if offset < md:
            break
        offset -= md

        if lm == m:
            lmd = leap_days(y)
            if offset < lmd:
                is_leap = True
                break
            offset -= lmd
        m += 1

    if m > 12:
        # Defensive fallback; should not happen, but avoids breaking delivery.
        m = 12
        offset = min(offset, 29)
    day = int(offset) + 1
    day = max(1, min(day, 30))
    lunar_text = f"农历{'闰' if is_leap else ''}{LUNAR_MONTHS[m-1]}月{LUNAR_DAYS[day-1]}"
    festival = LUNAR_FESTIVALS.get((m, day), '')
    dt = datetime.strptime(ymd, '%Y-%m-%d')
    term = SOLAR_TERMS.get((dt.month, dt.day), '')
    return {'lunar_date': lunar_text, 'lunar_month': m, 'lunar_day': day, 'lunar_festival': festival, 'solar_term': term}

def western_sign(dt):
    md = (dt.month, dt.day)
    prev = '摩羯'
    for boundary, sign in WEST_SIGNS:
        if md < boundary:
            return prev
        prev = sign
    return '摩羯'

def mystic_context(d):
    dt = datetime.strptime(d['target_date'], '%Y-%m-%d')
    days = (dt.date() - date(1900, 1, 31)).days
    ganzhi = GAN[(days + 6) % 10] + ZHI[(days + 0) % 12]
    lower = (d['lunar_month'] + d['lunar_day'] + d['weather_code']) % 8
    upper = (dt.month + dt.day + int(d['precip_prob'] or 0) + int(d['aqi'] or 0)) % 8
    lo, hi = BAGUA[lower], BAGUA[upper]
    hexagram = f"{hi[0]}上{lo[0]}下"
    star = western_sign(dt)
    # 皇极经世这里取“年月日气象象数”做轻量参考，不冒充严格命盘。
    huangji_num = (dt.year * 12 + dt.month + dt.day + d['lunar_day'] + int(d['aqi'] or 0)) % 64 + 1
    weather_force = '宜动' if d['precip_prob'] < 40 and d['wind_speed'] < 25 and (d['aqi'] or 0) <= 100 else '宜守'
    focus = '推进、沟通、曝光' if weather_force == '宜动' else '收敛、复盘、避险'
    line = f"{ganzhi}日｜星象{star}｜八卦{hexagram}（{hi[2]} / {lo[2]}）｜象数第{huangji_num}局，{weather_force}：{focus}。"
    return {'ganzhi_day': ganzhi, 'zodiac_sign': star, 'bagua_hexagram': hexagram, 'huangji_number': huangji_num, 'mystic_line': line}

def dynamic_life_tips(d):
    code, precip, feels, aqi, uv, wind, humidity = d['day_weather_code'], d['precip_prob'], d['feels'], d['aqi'] or 0, d['uv'], d['wind_speed'], d['humidity']
    lunar = d.get('lunar_date', '')
    marker = d.get('lunar_festival') or d.get('solar_term') or lunar
    gan = (d.get('ganzhi_day') or '甲子')[0]
    branch = (d.get('ganzhi_day') or '甲子')[1]
    hexagram = d.get('bagua_hexagram', '')
    star = d.get('zodiac_sign', '')
    huangji = int(d.get('huangji_number') or 1)

    element_hint = {
        '甲': ('木气生发', '多做拉伸、散步，别把计划憋在脑子里'), '乙': ('木气柔和', '适合细整理、轻沟通，别硬碰硬'),
        '丙': ('火气外放', '注意防晒降火，表达可以更直接'), '丁': ('火气内明', '适合专注创作，少熬夜耗神'),
        '戊': ('土气厚重', '适合收纳归位，饮食别太撑'), '己': ('土气调和', '适合稳步推进，照顾脾胃节律'),
        '庚': ('金气决断', '适合断舍离和定优先级，运动前充分热身'), '辛': ('金气精修', '适合精细打磨，少纠结细枝末节'),
        '壬': ('水气流动', '适合复盘和信息整理，注意保暖补水'), '癸': ('水气潜藏', '适合安静推进，避免情绪内耗'),
    }.get(gan, ('气象平稳', '按体感安排节奏'))
    branch_hint = {
        '子':'夜间少刷屏，睡眠优先', '丑':'脾胃和保暖优先', '寅':'适合早启动，但别急躁', '卯':'适合沟通协作',
        '辰':'注意湿气与拖延', '巳':'防晒降火，少上头', '午':'补水防暑，避开正午', '未':'适合整理家务与饮食节制',
        '申':'适合效率处理和断舍离', '酉':'适合精修细节', '戌':'注意收尾和边界', '亥':'适合复盘恢复体力',
    }.get(branch, '顺势安排作息')
    gua_hint = '沟通协作' if '兑' in hexagram or '巽' in hexagram else ('主动开局' if '乾' in hexagram or '震' in hexagram else ('止损沉淀' if '艮' in hexagram or '坎' in hexagram else '稳定承载'))
    star_hint = f"星象{star}偏向{'务实落地' if star in ('金牛','处女','摩羯') else ('表达连接' if star in ('双子','天秤','水瓶') else ('行动热度' if star in ('白羊','狮子','射手') else '照顾感受'))}"
    mystic_suffix = f"今日{element_hint[0]}，{branch_hint}；{star_hint}，卦象侧重{gua_hint}。"
    health_focus = f"象数第{huangji}局：{element_hint[1]}。"

    if precip >= 50 or code in (61,63,65,80,81,82,95,96,99):
        family = '家里备好雨伞和防滑鞋；老人小孩出门尽量走室内通道，回家及时擦干换衣。'
        food = '雨天湿气重，适合姜茶、热汤、清淡热食；少吃冰饮和太油腻的夜宵。'
        yi, ji = '整理室内、处理文档、早点收工', '赶路冒雨、鞋底打滑、临时改太多行程'
        todos = ['出门带伞并检查鞋底防滑', '重要文件/设备做好防水', '晚上早点洗热水澡休息']
    elif feels >= 28 or uv > 5:
        family = '提醒家人补水防晒；老人小孩避开正午暴晒，车内不要久留。'
        food = '天热偏晒，适合绿豆汤、淡盐水、蔬果和清淡蛋白；少冰饮猛灌。'
        yi, ji = '早晚运动、推进轻量计划、晒被通风', '正午暴晒、熬夜上火、情绪硬刚'
        todos = ['上午处理户外事项', '随身带水并做好防晒', '晚上复盘今天最重要的一件事']
    elif feels <= 10 or wind >= 25:
        family = '风冷明显，提醒家人加外套护颈；老人小孩早晚少在风口久站。'
        food = '偏冷或有风，适合热粥、汤面、姜枣茶；少吃生冷。'
        yi, ji = '保暖、收纳、复盘账目', '穿太薄、空腹吹风、拖到深夜'
        todos = ['早晚加一件外套', '热饮代替冰饮', '睡前把明日重点写下来']
    elif aqi > 100:
        family = '空气一般，敏感人群减少户外久待；家里短时通风即可，必要时戴口罩。'
        food = '空气偏差时多喝水，吃梨、银耳、绿叶菜；少烧烤油炸。'
        yi, ji = '室内专注、轻运动、清理桌面', '长时间路边跑步、开窗一整天、重口宵夜'
        todos = ['户外运动改室内或降低强度', '短时通风后关窗', '今晚早点睡保护呼吸道']
    else:
        family = '天气整体稳定，适合家人正常出行；早晚按体感加减薄外套。'
        food = '天气舒服，饮食以清淡均衡为主；多喝水，别用冰饮替代正餐。'
        yi, ji = '出行、沟通、推进计划', '拖延、久坐、晚上刷屏过久'
        todos = ['安排一段户外走动', '推进今天最值钱的一件事', '睡前减少屏幕时间']
    family = f"{family}{mystic_suffix}"
    food = f"{food}{'节气' + d['solar_term'] + '，' if d.get('solar_term') else ''}{'遇' + d['lunar_festival'] + '，' if d.get('lunar_festival') else ''}{branch_hint}，饮食别走极端。"
    act_good = f"{d.get('act_good','轻量活动')}；{gua_hint}"
    act_bad = f"{d.get('act_bad','过度消耗')}；{health_focus}"
    mystic = d.get('mystic_line', '')
    almanac = f"{marker}｜宜：{yi}；忌：{ji}。" + (f"<br>{mystic}" if mystic else '')
    return {'family_tip': family, 'food_tip': food, 'almanac_tip': almanac, 'todo_items': todos, 'act_good': act_good, 'act_bad': act_bad}

def resolve_city(city):
    city = (city or '上海').strip()
    city = CITY_ALIASES.get(city, city)
    if city not in CITY_COORDS:
        supported = '、'.join(sorted(CITY_COORDS))
        raise ValueError(f'暂不支持城市：{city}。当前支持：{supported}')
    return city, CITY_COORDS[city]

def parse_date(s, now=None):
    t = now or datetime.now()
    base = t.date()
    s = (s or 'today').strip().lower()
    if s in ('today','今天'):
        target = base
    elif s in ('tomorrow','明天'):
        target = base + timedelta(days=1)
    else:
        target = None
        for fmt in ('%Y-%m-%d','%m-%d'):
            try:
                parsed = datetime.strptime(s, fmt)
                if fmt == '%m-%d':
                    parsed = parsed.replace(year=t.year)
                    if parsed.date() < base:
                        parsed = parsed.replace(year=t.year + 1)
                target = parsed.date()
                break
            except ValueError:
                continue
        if target is None:
            raise ValueError(f'日期解析失败: {s}')

    days_ahead = (target - base).days
    if days_ahead < 0:
        raise ValueError(f'暂不支持历史天气：{target.isoformat()}')
    if days_ahead >= MAX_FORECAST_DAYS:
        raise ValueError(f'Open-Meteo 免费预报最多支持未来 {MAX_FORECAST_DAYS - 1} 天：{target.isoformat()}')
    return target.strftime('%Y-%m-%d'), days_ahead, t

def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent':'LunarWeather/1.0'})
    last_error = None
    timeouts = (10, 20, 30, 45)
    for attempt, timeout in enumerate(timeouts):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r: return json.loads(r.read().decode())
        except (ssl.SSLError, socket.timeout, urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            last_error = e
            if attempt < len(timeouts) - 1:
                time.sleep(min(8, 2 ** attempt))
    raise RuntimeError(f'天气数据请求失败: {last_error}')

def first_present(*values, default=0):
    for value in values:
        if value is not None:
            return value
    return default

def round_int(value, default=0):
    return round(first_present(value, default=default))

def pick_hourly(hourly, target_date):
    times = hourly.get('time', [])
    target_indices = [i for i, ts in enumerate(times) if ts.startswith(target_date)]
    if not target_indices:
        return {}

    for hour in ('09:00', '12:00', '15:00', '18:00'):
        for idx in target_indices:
            if times[idx].endswith(hour):
                return {k: (v[idx] if isinstance(v, list) and idx < len(v) else v) for k, v in hourly.items()}

    idx = target_indices[len(target_indices) // 2]
    return {k: (v[idx] if isinstance(v, list) and idx < len(v) else v) for k, v in hourly.items()}

def main():
    city = sys.argv[1] if len(sys.argv)>1 else '上海'
    date_str = sys.argv[2] if len(sys.argv)>2 else 'today'
    target, days_ahead, date_obj = parse_date(date_str)
    city, (lat, lon) = resolve_city(city)
    now = datetime.now()

    # daily forecast for target day
    daily = fetch(f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max,weathercode,sunrise,sunset&timezone=auto&forecast_days={days_ahead+1}')
    daily_times = daily['daily']['time']
    if target not in daily_times:
        raise RuntimeError(f'未拿到目标日期预报：{target}')
    didx = daily_times.index(target)
    max_t = daily['daily']['temperature_2m_max'][didx]
    min_t = daily['daily']['temperature_2m_min'][didx]
    precip = first_present(daily['daily']['precipitation_probability_max'][didx], default=0)
    day_code = daily['daily']['weathercode'][didx]
    sunrise = daily['daily'].get('sunrise', [''])[didx] if daily['daily'].get('sunrise') else ''
    sunset = daily['daily'].get('sunset', [''])[didx] if daily['daily'].get('sunset') else ''

    if days_ahead == 0:
        cu = fetch(f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,apparent_temperature,relativehumidity_2m,weathercode,windspeed_10m,uv_index&timezone=auto')
        c = cu['current']
        code = first_present(c.get('weathercode'), day_code)
        temp = first_present(c.get('temperature_2m'), (max_t + min_t) / 2)
        feels = first_present(c.get('apparent_temperature'), temp)
        humidity = first_present(c.get('relativehumidity_2m'), default=0)
        wind = first_present(c.get('windspeed_10m'), default=0)
        uv = first_present(c.get('uv_index'), default=0)
        is_night = now.hour < 6 or now.hour >= 19
    else:
        hourly = fetch(f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,apparent_temperature,relativehumidity_2m,weathercode,windspeed_10m,uv_index&timezone=auto&forecast_days={days_ahead+1}')
        h = pick_hourly(hourly.get('hourly', {}), target)
        code = first_present(day_code, h.get('weathercode'))
        temp = first_present(h.get('temperature_2m'), (max_t + min_t) / 2)
        feels = first_present(h.get('apparent_temperature'), temp)
        humidity = first_present(h.get('relativehumidity_2m'), default=0)
        wind = first_present(h.get('windspeed_10m'), default=0)
        uv = first_present(h.get('uv_index'), default=0)
        is_night = False

    emoji, desc = WEATHER_CODES.get(code, ('🌡️', '未知'))
    if is_night and code in W_CODE_NIGHT: emoji = W_CODE_NIGHT[code]

    # air quality
    aq = {}
    try:
        if days_ahead == 0:
            aq = fetch(f'https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=us_aqi,pm2_5,pm10,ozone,nitrogen_dioxide&timezone=auto')
            aq_current = aq.get('current', {})
        else:
            aq = fetch(f'https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&hourly=us_aqi,pm2_5,nitrogen_dioxide&timezone=auto&forecast_days={days_ahead+1}')
            aq_current = pick_hourly(aq.get('hourly', {}), target)
        aqi = aq_current.get('us_aqi')
    except Exception:
        aq_current = {}
        aqi = None
    aqi_emoji, aqi_label_str = aqi_label(aqi)
    pm25 = aq_current.get('pm2_5')
    no2 = aq_current.get('nitrogen_dioxide')

    # UV
    uv_desc = next((lbl for thresh,lbl,_ in UV_LEVELS if uv<=thresh), '极强')

    # activity suggestions
    if feels < 5: act_good, act_bad = '室内瑜伽/健身房', '户外跑步'
    elif feels < 15: act_good, act_bad = '快走/慢跑', '大量出汗户外运动'
    elif feels < 25: act_good, act_bad = '跑步/骑行/球类', '正午暴晒下长时间户外'
    elif feels < 32: act_good, act_bad = '游泳/早晚户外', '正午户外暴晒'
    else: act_good, act_bad = '室内运动/游泳', '户外剧烈运动'

    # dressing
    if feels < 5: cloth = '厚羽绒服+保暖内衣'
    elif feels < 12: cloth = '棉服/风衣+毛衣'
    elif feels < 18: cloth = '薄外套+长袖'
    elif feels < 25: cloth = '长袖/薄衬衫'
    else: cloth = '短袖+防晒'

    # keywords
    kw = [desc, wind_desc(wind), aqi_label_str if aqi else '空气良好']

    result = {
        'city': city, 'target_date': target, 'days_ahead': days_ahead,
        'date_obj': target,
        'emoji': emoji, 'weather_desc': desc,
        'is_night': is_night,
        'temp': round_int(temp), 'feels': round_int(feels),
        'humidity': round_int(humidity),
        'wind_speed': round_int(wind), 'wind_desc': wind_desc(wind),
        'max_temp': round(max_t), 'min_temp': round(min_t),
        'precip_prob': precip,
        'uv': uv, 'uv_level': uv_desc,
        'aqi': aqi, 'aqi_emoji': aqi_emoji, 'aqi_label': aqi_label_str, 'aqi_standard': 'US AQI',
        'pm25': pm25, 'no2': no2,
        'weather_code': code, 'day_weather_code': day_code,
        'sunrise': sunrise, 'sunset': sunset,
        'alert': get_alert(code, precip),
        'keywords': kw,
        'act_good': act_good, 'act_bad': act_bad,
        'cloth': cloth,
    }
    result.update(lunar_info_for(target))
    result.update(mystic_context(result))
    result.update(dynamic_life_tips(result))
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f'天气数据获取失败：{e}', file=sys.stderr)
        sys.exit(1)
