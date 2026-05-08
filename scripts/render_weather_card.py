#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render Lunar Weather HTML card to PNG.
Usage: python3 render_weather_card.py <城市> [today|YYYY-MM-DD]
"""
import json, subprocess, sys, os, html, tempfile, pathlib, re
from datetime import datetime

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / 'scripts' / 'get_weather_data.py'
OUTDIR = ROOT / 'outputs'
OUTDIR.mkdir(exist_ok=True)

THEME_MAP = {
    'sunny': ((0,1), 'sunny-day', 'sunny-night'),
    'cloudy': ((2,3), 'cloudy-day', 'cloudy-night'),
    'fog': ((45,48), 'fog', 'fog'),
    'rain': ((51,53,55,56,57,61,63,65,66,67,80,81,82), 'rain-day', 'rain-night'),
    'snow': ((71,73,75,77,85,86), 'snow', 'snow'),
    'storm': ((95,96,99), 'storm', 'storm'),
}

def theme(code, night):
    for _, (codes, day, nite) in THEME_MAP.items():
        if code in codes: return nite if night else day
    return 'cloudy-night' if night else 'cloudy-day'

def esc(x): return html.escape(str(x))

def score(d):
    s = 85
    if d['precip_prob'] and d['precip_prob'] > 50: s -= 15
    if d['aqi'] and d['aqi'] > 100: s -= 15
    if d['feels'] < 5 or d['feels'] > 32: s -= 15
    return max(40, min(96, s))

def quote_for(d):
    if d['weather_code'] in (0,1):
        return 'Keep your face always toward the sunshine, and shadows will fall behind you.<br>把脸迎向阳光，阴影自然会落在身后。—— Walt Whitman'
    if d['weather_code'] in (2,3):
        return 'Adopt the pace of nature: her secret is patience.<br>跟随自然的节奏；她的秘密是耐心。—— Ralph Waldo Emerson'
    if d['weather_code'] in (51,53,55,61,63,65,80,81,82):
        return 'Some people feel the rain. Others just get wet.<br>有人感受雨，有人只是被淋湿。—— Bob Marley'
    return 'The day is what you make it, so make it a good one.<br>日子会成为你塑造的样子，所以把它过好。'

def build_html(d):
    th = theme(d['weather_code'], d['is_night'])
    sc = score(d)
    bar = sc
    kw = ''.join(f'<span class="chip">{esc(k)}</span>' for k in d['keywords'])
    now = datetime.now().strftime('%H:%M')
    summary = f"今晚{d['weather_desc']}，体感约 {d['feels']}℃；{d['wind_desc']}，空气{d['aqi_label']}。薄外套是最稳选择。" if d['is_night'] else f"今天{d['weather_desc']}，{d['min_temp']}–{d['max_temp']}℃；降水概率 {d['precip_prob']}%，空气{d['aqi_label']}。"
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<style>
*{{box-sizing:border-box}}html,body{{margin:0;padding:0;background:#eef3fb}}body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif;padding:24px;color:#1f2937}}.wrap{{width:540px;margin:0 auto;background:linear-gradient(180deg,#f8fbff,#f4f7fb);border-radius:28px;padding:18px;box-shadow:0 22px 60px rgba(31,45,61,.16)}}.hero{{position:relative;overflow:hidden;border-radius:24px;padding:22px 20px 20px;color:#fff;box-shadow:0 14px 28px rgba(59,130,246,.20)}}.sunny-day{{background:linear-gradient(135deg,#38bdf8,#60a5fa 42%,#fbbf24)}}.sunny-night{{background:linear-gradient(135deg,#0f172a,#1e3a8a 55%,#7c3aed)}}.cloudy-day{{background:linear-gradient(135deg,#93c5fd,#94a3b8 54%,#cbd5e1)}}.cloudy-night{{background:linear-gradient(135deg,#334155,#475569 48%,#64748b)}}.rain-day{{background:linear-gradient(135deg,#2563eb,#0ea5e9 48%,#64748b)}}.rain-night{{background:linear-gradient(135deg,#0f172a,#1e40af 55%,#334155)}}.snow{{background:linear-gradient(135deg,#bae6fd,#e0f2fe 52%,#f8fafc);color:#334155}}.storm{{background:linear-gradient(135deg,#18181b,#4c1d95 55%,#facc15 115%)}}.fog{{background:linear-gradient(135deg,#94a3b8,#cbd5e1 55%,#e2e8f0);color:#334155}}.hero:after{{content:"";position:absolute;right:-42px;top:-48px;width:150px;height:150px;border-radius:50%;background:rgba(255,255,255,.22)}}.hero:before{{content:"";position:absolute;right:42px;bottom:-55px;width:130px;height:130px;border-radius:50%;background:rgba(255,255,255,.13)}}.hero-top{{position:relative;z-index:1;display:flex;align-items:center;justify-content:space-between;gap:12px}}.city{{font-size:23px;font-weight:900}}.badge{{font-size:13px;font-weight:700;background:rgba(255,255,255,.2);border:1px solid rgba(255,255,255,.25);padding:7px 10px;border-radius:999px;backdrop-filter:blur(6px)}}.date{{position:relative;z-index:1;margin-top:8px;font-size:14px;opacity:.92}}.temp{{position:relative;z-index:1;margin-top:18px;display:flex;align-items:flex-end;gap:12px}}.temp-main{{font-size:54px;font-weight:900;line-height:.9}}.temp-sub{{font-size:15px;line-height:1.55;opacity:.96;padding-bottom:3px}}.summary{{position:relative;z-index:1;margin-top:14px;font-size:15px;line-height:1.55;background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.18);padding:10px 12px;border-radius:16px}}.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:14px}}.section{{background:rgba(255,255,255,.86);border:1px solid rgba(148,163,184,.16);border-radius:22px;padding:14px 14px 13px;box-shadow:0 8px 22px rgba(15,23,42,.055)}}.section.full{{grid-column:1/-1}}.head{{display:flex;align-items:center;gap:9px;margin-bottom:9px}}.ico{{width:34px;height:34px;border-radius:13px;display:flex;align-items:center;justify-content:center;font-size:19px;box-shadow:inset 0 0 0 1px rgba(255,255,255,.55)}}.h{{font-size:15px;font-weight:900;color:#111827}}.body{{font-size:14px;line-height:1.65;color:#374151}}.muted{{color:#64748b}}.chips{{display:flex;flex-wrap:wrap;gap:7px}}.chip{{padding:6px 9px;border-radius:999px;background:#f1f5f9;font-size:13px;font-weight:700;color:#334155}}.score{{display:flex;align-items:center;gap:10px}}.score-num{{font-size:30px;font-weight:900;color:#2563eb}}.bar{{height:8px;border-radius:999px;background:#e2e8f0;overflow:hidden;flex:1}}.bar span{{display:block;height:100%;width:{bar}%;border-radius:999px;background:linear-gradient(90deg,#60a5fa,#34d399)}}.warn{{background:linear-gradient(135deg,#fff7ed,#fff1f2)}}.feel{{background:linear-gradient(135deg,#ecfeff,#f0fdf4)}}.commute{{background:linear-gradient(135deg,#fff7ed,#fffbeb)}}.air{{background:linear-gradient(135deg,#f5f3ff,#eef2ff)}}.health{{background:linear-gradient(135deg,#f8fafc,#fefce8)}}.family{{background:linear-gradient(135deg,#eff6ff,#f8fafc)}}.food{{background:linear-gradient(135deg,#f0fdf4,#ecfdf5)}}.mystic{{background:linear-gradient(135deg,#faf5ff,#fdf2f8)}}.todo{{background:linear-gradient(135deg,#fffbeb,#fef3c7)}}.final{{margin-top:12px;border-radius:22px;padding:16px 15px;color:#334155;background:linear-gradient(135deg,#fff7ed,#ecfeff 52%,#f0fdf4);border:1px solid rgba(148,163,184,.18);box-shadow:0 10px 24px rgba(15,23,42,.07);font-size:15px;font-weight:800;line-height:1.65}}.quote{{margin-top:8px;padding-top:8px;border-top:1px dashed rgba(100,116,139,.28);font-size:13px;font-weight:700;color:#64748b;line-height:1.55}}.footer{{text-align:center;color:#94a3b8;font-size:12px;margin-top:12px}}
</style></head><body><div class="wrap"><div class="hero {th}"><div class="hero-top"><div class="city">{d['emoji']} {esc(d['city'])}天气卡</div><div class="badge">{esc(d['weather_desc'])} · {'夜间' if d['is_night'] else '白天'}</div></div><div class="date">{esc(d['target_date'])}｜{now} 更新</div><div class="temp"><div class="temp-main">{d['temp']}°</div><div class="temp-sub">{esc(d['weather_desc'])}｜体感 {d['feels']}℃<br>空气{esc(d['aqi_label'])}｜{esc(d['wind_desc'])}</div></div><div class="summary">{esc(summary)}</div></div><div class="grid2"><div class="section"><div class="head"><div class="ico" style="background:#fff7cc">✨</div><div class="h">今日关键词</div></div><div class="chips">{kw}</div></div><div class="section"><div class="head"><div class="ico" style="background:#dbeafe">📊</div><div class="h">综合指数</div></div><div class="score"><div class="score-num">{sc}</div><div class="bar"><span></span></div></div><div class="body muted">适合轻量出行</div></div><div class="section full warn"><div class="head"><div class="ico" style="background:#fee2e2">🚨</div><div class="h">重要预警</div></div><div class="body">{esc(d['alert'])}</div></div><div class="section feel"><div class="head"><div class="ico" style="background:#cffafe">🌡️</div><div class="h">天气体感</div></div><div class="body">{esc(d['weather_desc'])}｜{d['min_temp']}–{d['max_temp']}℃<br>体感 {d['feels']}℃<br><span class="muted">湿度 {d['humidity']}%，风速 {d['wind_speed']}km/h。</span></div></div><div class="section commute"><div class="head"><div class="ico" style="background:#fed7aa">🧥</div><div class="h">通勤穿搭</div></div><div class="body">{esc(d['cloth'])}<br>降水概率 {d['precip_prob']}%；{'带伞更稳。' if d['precip_prob']>40 else '正常出行即可。'}</div></div><div class="section air"><div class="head"><div class="ico" style="background:#ede9fe">🍃</div><div class="h">空气紫外线</div></div><div class="body">AQI {d['aqi'] or '—'}｜{esc(d['aqi_label'])}<br>UV {d['uv']}｜{esc(d['uv_level'])}<br><span class="muted">PM2.5 {d['pm25'] or '—'}</span></div></div><div class="section health"><div class="head"><div class="ico" style="background:#fef9c3">🏃</div><div class="h">健康活动</div></div><div class="body">适合：{esc(d['act_good'])}<br>不建议：{esc(d['act_bad'])}<br>运动后注意别吹风。</div></div><div class="section family"><div class="head"><div class="ico" style="background:#dbeafe">👨‍👩‍👧</div><div class="h">家庭提醒</div></div><div class="body">老人小孩按体感增减衣物；敏感人群关注空气变化。</div></div><div class="section food"><div class="head"><div class="ico" style="background:#dcfce7">🍵</div><div class="h">饮食建议</div></div><div class="body">适合温热饮食，少冰饮；热茶或温水更舒服。</div></div><div class="section mystic"><div class="head"><div class="ico" style="background:#f3e8ff">🧭</div><div class="h">宜忌参考</div></div><div class="body">宜：整理计划、复盘、轻运动<br>忌：拖延、熬夜硬扛</div></div><div class="section todo"><div class="head"><div class="ico" style="background:#fef3c7">🔥</div><div class="h">今日三件事</div></div><div class="body">1. 出门看体感<br>2. 根据降水带伞<br>3. 睡前少看屏幕</div></div></div><div class="final">💡 一句话建议：{esc(summary)}<div class="quote">📖 今日小句：{quote_for(d)}</div></div><div class="footer">Lunar Weather｜自动生成，仅供生活参考</div></div></body></html>'''

def main():
    city = sys.argv[1] if len(sys.argv)>1 else 'Shanghai'
    date = sys.argv[2] if len(sys.argv)>2 else 'today'
    raw = subprocess.check_output([sys.executable, str(DATA), city, date], text=True)
    d = json.loads(raw)
    html_text = build_html(d)
    slug = f"weather-card-{d['city']}-{d['target_date']}"
    html_path = OUTDIR / f'{slug}.html'
    png_path = OUTDIR / f'{slug}.png'
    html_path.write_text(html_text, encoding='utf-8')
    edge = '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge'
    subprocess.check_call([edge, '--headless', '--disable-gpu', '--hide-scrollbars', f'--screenshot={png_path}', '--window-size=640,1380', 'file://' + str(html_path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(json.dumps({'html': str(html_path), 'png': str(png_path), 'data': d}, ensure_ascii=False, indent=2))

if __name__ == '__main__': main()
