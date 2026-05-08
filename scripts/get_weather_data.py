#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lunar-weather: 获取天气数据（Open-Meteo，无需 API key）
用法: python3 get_weather_data.py <城市> [YYYY-MM-DD| today| tomorrow]
"""
import sys, json, urllib.request, os
from datetime import datetime

CITY_COORDS = {
    'Shanghai': (31.2304, 121.4737), '北京': (39.9042, 116.4074),
    '上海': (31.2304, 121.4737), '南京': (32.0603, 118.7969),
    '杭州': (30.2741, 120.1551), '苏州': (31.2989, 120.5853),
    '广州': (23.1291, 113.2644), '深圳': (22.5431, 114.0579),
    '成都': (30.5728, 104.0668), '武汉': (30.5928, 114.3055),
    '西安': (34.3416, 108.9398), '重庆': (29.4316, 106.9123),
    '东京': (35.6762, 139.6503), '香港': (22.3193, 114.1694),
}

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

def parse_date(s):
    t = datetime.now()
    s = s.strip().lower()
    if s in ('today','今天'): return t.strftime('%Y-%m-%d'), 0, t
    if s in ('tomorrow','明天'): return (t.replace(hour=0)+__import__("datetime").timedelta(1)).strftime('%Y-%m-%d'), 1, t
    for fmt in ('%Y-%m-%d','%m-%d'):
        try: p = datetime.strptime(s, fmt).replace(year=t.year); return p.strftime('%Y-%m-%d'), max(0,(p-t).days), p
        except: pass
    raise ValueError(f'日期解析失败: {s}')

def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent':'LunarWeather/1.0'})
    with urllib.request.urlopen(req, timeout=10) as r: return json.loads(r.read().decode())

def main():
    city = sys.argv[1] if len(sys.argv)>1 else 'Shanghai'
    date_str = sys.argv[2] if len(sys.argv)>2 else 'today'
    target, days_ahead, date_obj = parse_date(date_str)
    lat, lon = CITY_COORDS.get(city, CITY_COORDS['Shanghai'])
    now = datetime.now()

    # current weather
    cu = fetch(f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,apparent_temperature,relativehumidity_2m,weathercode,windspeed_10m,uv_index&timezone=auto')
    c = cu['current']
    code = c['weathercode']
    emoji, desc = WEATHER_CODES.get(code, ('🌡️', '未知'))
    is_night = now.hour < 6 or now.hour >= 19
    if is_night and code in W_CODE_NIGHT: emoji = W_CODE_NIGHT[code]

    # daily forecast for target day
    daily = fetch(f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max,weathercode,sunrise,sunset&timezone=auto&forecast_days={min(days_ahead+1,7)}')
    didx = days_ahead if days_ahead < len(daily['daily']['time']) else 0
    max_t = daily['daily']['temperature_2m_max'][didx]
    min_t = daily['daily']['temperature_2m_min'][didx]
    precip = daily['daily']['precipitation_probability_max'][didx]
    day_code = daily['daily']['weathercode'][didx]
    sunrise = daily['daily'].get('sunrise', [''])[didx] if daily['daily'].get('sunrise') else ''
    sunset = daily['daily'].get('sunset', [''])[didx] if daily['daily'].get('sunset') else ''

    # air quality
    try:
        aq = fetch(f'https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=us_aqi,pm2_5,pm10,ozone,nitrogen_dioxide&timezone=auto')
        aqi = aq['current'].get('us_aqi')
    except: aqi = None
    aqi_emoji, aqi_label_str = aqi_label(aqi)
    pm25 = aq['current'].get('pm2_5') if 'current' in aq else None
    no2 = aq['current'].get('nitrogen_dioxide') if 'current' in aq else None

    # UV
    uv = c.get('uv_index', 0)
    uv_desc = next((lbl for thresh,lbl,_ in UV_LEVELS if uv<=thresh), ('强','涂防晒+遮阳'))

    # activity suggestions
    feels = c.get('apparent_temperature', c['temperature_2m'])
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
    kw = [desc, wind_desc(c['windspeed_10m']), aqi_label_str if aqi else '空气良好']

    result = {
        'city': city, 'target_date': target, 'days_ahead': days_ahead,
        'date_obj': target,
        'emoji': emoji, 'weather_desc': desc,
        'is_night': is_night,
        'temp': round(c['temperature_2m']), 'feels': round(c['apparent_temperature']),
        'humidity': c['relativehumidity_2m'],
        'wind_speed': round(c['windspeed_10m']), 'wind_desc': wind_desc(c['windspeed_10m']),
        'max_temp': round(max_t), 'min_temp': round(min_t),
        'precip_prob': precip,
        'uv': uv, 'uv_level': uv_desc,
        'aqi': aqi, 'aqi_emoji': aqi_emoji, 'aqi_label': aqi_label_str,
        'pm25': pm25, 'no2': no2,
        'weather_code': code, 'day_weather_code': day_code,
        'sunrise': sunrise, 'sunset': sunset,
        'alert': get_alert(code, precip),
        'keywords': kw,
        'act_good': act_good, 'act_bad': act_bad,
        'cloth': cloth,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
