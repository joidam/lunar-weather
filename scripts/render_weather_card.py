#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render Lunar Weather card to PNG.

Usage:
  python3 scripts/render_weather_card.py 上海 [today|YYYY-MM-DD]
"""
import html
import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "scripts" / "get_weather_data.py"
OUTDIR = ROOT / "outputs"
OUTDIR.mkdir(exist_ok=True)
QUOTE_HISTORY = OUTDIR / "quote-history.json"

THEME_MAP = {
    "sunny": ((0, 1), "sunny-day", "sunny-night"),
    "cloudy": ((2, 3), "cloudy-day", "cloudy-night"),
    "fog": ((45, 48), "fog", "fog"),
    "rain": ((51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82), "rain-day", "rain-night"),
    "snow": ((71, 73, 75, 77, 85, 86), "snow", "snow"),
    "storm": ((95, 96, 99), "storm", "storm"),
}


def theme(code, night):
    for _, (codes, day, nite) in THEME_MAP.items():
        if code in codes:
            return nite if night else day
    return "cloudy-night" if night else "cloudy-day"


def esc(value):
    return html.escape(str(value))


def score(d):
    value = 85
    if d["precip_prob"] and d["precip_prob"] > 50:
        value -= 15
    if d["aqi"] and d["aqi"] > 100:
        value -= 15
    if d["feels"] < 5 or d["feels"] > 32:
        value -= 15
    return max(40, min(96, value))


QUOTE_POOLS = {
    "sunny": [
        "光线不错，别只晒太阳，也晒晒计划。",
        "天亮得干净，手上的事也适合干脆推进。",
        "今天适合把心气抬起来，先完成一件小而确定的事。",
        "晴天别浪费，留一点时间给行动。",
        "阳光只是提醒：好状态也要靠自己维护。",
        "天气给了亮色，剩下的交给执行力。",
        "把节奏放稳，今天会比想象中顺一点。",
        "适合抬头看天，也适合低头把事做完。",
    ],
    "cloudy": [
        "云多不代表没光，事情慢一点也能往前走。",
        "今天适合沉住气，把复杂的事拆小。",
        "不用等状态全晴，先把第一步做了。",
        "灰一点的天气，正好适合安静打磨。",
        "节奏可以慢，方向别散。",
        "今天别急着证明，先把基础铺实。",
        "云层会变，计划也要留一点弹性。",
        "适合少说多做，把心思收回来。",
    ],
    "rain": [
        "雨声适合慢下来，但事情别跟着停。",
        "带伞是生活，推进是态度。",
        "雨天不硬冲，换个稳一点的打法。",
        "今天适合收拢心神，把能控的部分做好。",
        "路面湿滑，决策也别急转弯。",
        "雨会落下去，事情也会一件件落地。",
        "别和天气较劲，和拖延较劲。",
        "潮湿的日子，最需要清爽的安排。",
    ],
    "storm": [
        "天气不稳时，先保安全，再谈效率。",
        "今天别硬扛，把风险放在第一位。",
        "风雨大的时候，守住节奏就是赢。",
        "能推迟的推迟，必须做的做扎实。",
    ],
    "fog": [
        "看不远的时候，就把眼前一步走稳。",
        "雾天慢一点，判断清楚一点。",
        "视线不清，计划更要清楚。",
        "今天适合减少干扰，专注眼前。",
    ],
    "snow": [
        "冷一点没关系，心里的火别灭。",
        "雪天适合慢行，也适合认真收尾。",
        "把保暖做好，把节奏守住。",
        "冷天别逞强，稳稳当当更值钱。",
    ],
    "hot": [
        "天热容易烦，越要把事情排清楚。",
        "今天别和高温硬拼，效率要靠节奏。",
        "少一点躁，多一点水和耐心。",
        "热归热，关键动作别断。",
    ],
    "cold": [
        "该添衣添衣，该收心收心，稳一点不吃亏。",
        "冷天适合把计划做得更紧凑。",
        "保暖不是小事，状态也是生产力。",
        "别让低温偷走行动力。",
    ],
    "air": [
        "今天少和空气硬刚，把精力留给更值钱的事。",
        "空气一般，安排就更要聪明一点。",
        "少在外面耗，多在里面做成点东西。",
        "环境不理想时，更要保护好自己的状态。",
    ],
    "solar_term": [
        "顺着节气调整节奏，比硬冲更聪明。",
        "节气在变，人也要会换打法。",
        "今天适合顺势而为，别把自己拧太紧。",
        "时令提醒我们：稳住，比拉满更长久。",
    ],
    "weekend": [
        "休息不是摆烂，是给下周攒一点胜率。",
        "周末也可以轻轻推进一点，不必用力过猛。",
        "给身体一点余地，给目标一点进度。",
        "今天适合慢下来，但别完全散掉。",
    ],
    "month_start": [
        "月初别急着许愿，先把账和计划摊开。",
        "新的月份，先定规则，再拼速度。",
        "开局不用猛，方向要准。",
        "月初最值钱的是清醒，不是热血。",
    ],
    "month_end": [
        "月底适合复盘，别让经验白白过去。",
        "收尾做漂亮，下个月才好起势。",
        "今天适合清账、清单、清脑子。",
        "把这个月捋清楚，就是给下个月铺路。",
    ],
    "default": [
        "日子不会自动变好，但你可以每天多赢一点。",
        "把今天过稳，就是在给未来加筹码。",
        "少一点空想，多一个完成。",
        "今天不求惊艳，求扎实。",
        "别被情绪带着跑，让清单带着你走。",
        "能量有限，先给最重要的事。",
        "把一件小事做好，胜过想十件大事。",
        "稳住基本盘，机会才接得住。",
    ],
}


def quote_categories(d):
    code = d["weather_code"]
    categories = []
    if code in (0, 1):
        categories.append("sunny")
    elif code in (2, 3):
        categories.append("cloudy")
    elif code in (45, 48):
        categories.append("fog")
    elif code in (51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82):
        categories.append("rain")
    elif code in (71, 73, 75, 77, 85, 86):
        categories.append("snow")
    elif code in (95, 96, 99):
        categories.append("storm")

    if d.get("feels") is not None:
        if d["feels"] >= 31:
            categories.append("hot")
        elif d["feels"] <= 6:
            categories.append("cold")
    if d.get("aqi") and d["aqi"] > 100:
        categories.append("air")
    if d.get("solar_term"):
        categories.append("solar_term")

    try:
        dt = datetime.strptime(d["target_date"], "%Y-%m-%d")
        if dt.weekday() >= 5:
            categories.append("weekend")
        if dt.day <= 3:
            categories.append("month_start")
        elif dt.day >= 27:
            categories.append("month_end")
    except ValueError:
        pass

    categories.append("default")
    return categories


def load_quote_history():
    try:
        data = json.loads(QUOTE_HISTORY.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {"records": []}
    if not isinstance(data, dict) or not isinstance(data.get("records"), list):
        return {"records": []}
    return data


def save_quote_history(history):
    records = history.get("records", [])[-60:]
    QUOTE_HISTORY.write_text(json.dumps({"records": records}, ensure_ascii=False, indent=2), encoding="utf-8")


def quote_for(d):
    history = load_quote_history()
    records = history["records"]
    key = f"{d.get('city', '')}:{d.get('target_date', '')}"
    for record in records:
        if record.get("key") == key and record.get("quote"):
            return record["quote"]

    recent = {record.get("quote") for record in records[-30:]}
    candidates = []
    for category in quote_categories(d):
        for quote in QUOTE_POOLS.get(category, []):
            candidates.append((category, quote))

    unique_candidates = []
    seen = set()
    for category, quote in candidates:
        if quote not in seen:
            unique_candidates.append((category, quote))
            seen.add(quote)

    seed = f"{key}:{d.get('weather_code')}:{d.get('solar_term', '')}:{d.get('aqi', '')}"
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    start = int(digest[:8], 16) % max(1, len(unique_candidates))
    ordered = unique_candidates[start:] + unique_candidates[:start]
    category, quote = next(((c, q) for c, q in ordered if q not in recent), ordered[0])

    records.append({
        "key": key,
        "date": d.get("target_date"),
        "city": d.get("city"),
        "category": category,
        "quote": quote,
    })
    history["records"] = records[-60:]
    save_quote_history(history)
    return quote


def final_line_for(d):
    return f"今日小句：{quote_for(d)}"


def summary_for(d):
    if d["is_night"]:
        return f"今晚{d['weather_desc']}，体感约 {d['feels']}℃；{d['wind_desc']}，空气{d['aqi_label']}。薄外套是稳选择。"
    return f"今天{d['weather_desc']}，{d['min_temp']}–{d['max_temp']}℃；降水概率 {d['precip_prob']}%，空气{d['aqi_label']}。"


def build_html(d):
    th = theme(d["weather_code"], d["is_night"])
    sc = score(d)
    alert_text = d.get("alert", "")
    has_alert = bool(alert_text and not alert_text.startswith("✅"))
    kw = "".join(f'<span class="chip">{esc(k)}</span>' for k in d["keywords"])
    if has_alert:
        kw += f'<span class="chip alert-chip">{esc(alert_text)}</span>'
    now = datetime.now().strftime("%H:%M")
    lunar_line = "｜".join(x for x in (d.get("lunar_date"), d.get("solar_term"), d.get("lunar_festival")) if x)
    summary = summary_for(d)
    aqi_title = esc(d.get("aqi_standard", "AQI"))
    return f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"/><meta name="viewport" content="width=540,initial-scale=1"/>
<style>
*{{box-sizing:border-box}}html,body{{margin:0;padding:0;background:#eef3fb;width:540px}}body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;color:#1f2937;zoom:2;transform-origin:top left}}:root{{--font-body:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;--font-display:'Songti SC','STSong',Georgia,serif}}.wrap{{width:540px;margin:0;background:linear-gradient(180deg,#f8fbff,#f4f7fb);border-radius:28px;padding:18px;box-shadow:0 22px 60px rgba(31,45,61,.16)}}.hero{{position:relative;overflow:hidden;border-radius:24px;padding:22px 20px 20px;color:#fff;box-shadow:0 14px 28px rgba(59,130,246,.20)}}.sunny-day{{background:linear-gradient(135deg,#38bdf8,#60a5fa 42%,#fbbf24)}}.sunny-night{{background:linear-gradient(135deg,#0f172a,#1e3a8a 55%,#7c3aed)}}.cloudy-day{{background:linear-gradient(135deg,#93c5fd,#94a3b8 54%,#cbd5e1)}}.cloudy-night{{background:linear-gradient(135deg,#334155,#475569 48%,#64748b)}}.rain-day{{background:linear-gradient(135deg,#2563eb,#0ea5e9 48%,#64748b)}}.rain-night{{background:linear-gradient(135deg,#0f172a,#1e40af 55%,#334155)}}.snow{{background:linear-gradient(135deg,#bae6fd,#e0f2fe 52%,#f8fafc);color:#334155}}.storm{{background:linear-gradient(135deg,#18181b,#4c1d95 55%,#facc15 115%)}}.fog{{background:linear-gradient(135deg,#94a3b8,#cbd5e1 55%,#e2e8f0);color:#334155}}.hero:after{{content:"";position:absolute;right:-42px;top:-48px;width:150px;height:150px;border-radius:50%;background:rgba(255,255,255,.22)}}.hero:before{{content:"";position:absolute;right:42px;bottom:-55px;width:130px;height:130px;border-radius:50%;background:rgba(255,255,255,.13)}}.hero>*{{position:relative;z-index:1}}.hero-top{{display:flex;align-items:center;justify-content:space-between;gap:12px}}.city{{font-family:var(--font-display);font-size:34px;font-weight:600;letter-spacing:2px;text-shadow:0 2px 8px rgba(0,0,0,.13)}}.badge{{font-size:13px;font-weight:700;background:rgba(255,255,255,.2);border:1px solid rgba(255,255,255,.25);padding:7px 10px;border-radius:999px;backdrop-filter:blur(6px)}}.date{{margin-top:8px;font-size:14px;opacity:.92}}.temp{{margin-top:18px;display:flex;align-items:flex-end;gap:12px}}.temp-main{{font-family:Georgia,serif;font-size:62px;font-weight:500;line-height:.9;text-shadow:0 2px 10px rgba(0,0,0,.10)}}.temp-sub{{font-size:15px;line-height:1.55;opacity:.96;padding-bottom:3px}}.summary{{margin-top:14px;font-size:15px;line-height:1.55;background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.18);padding:10px 12px;border-radius:16px}}.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:14px}}.section{{background:rgba(255,255,255,.88);border:1px solid rgba(148,163,184,.18);border-radius:22px;padding:14px;box-shadow:0 8px 22px rgba(15,23,42,.055);min-height:116px}}.section.full{{grid-column:1/-1}}.head{{display:flex;align-items:center;gap:9px;margin-bottom:9px}}.ico{{width:34px;height:34px;border-radius:13px;display:flex;align-items:center;justify-content:center;font-size:19px;box-shadow:inset 0 0 0 1px rgba(255,255,255,.55)}}.h{{font-family:var(--font-display);font-size:18px;font-weight:600;color:#4b3528;letter-spacing:.8px}}.body{{font-size:14px;line-height:1.65;color:#374151;overflow-wrap:anywhere}}.muted{{color:#64748b}}.chips{{display:flex;flex-wrap:wrap;gap:7px}}.chip{{padding:6px 9px;border-radius:999px;background:#f1f5f9;font-size:13px;font-weight:700;color:#334155}}.alert-chip{{background:#fff1f2;color:#be123c;border:1px solid rgba(244,63,94,.22);flex-basis:100%;line-height:1.45}}.score{{display:flex;align-items:center;gap:10px}}.score-num{{font-family:Georgia,serif;font-size:38px;font-weight:500;color:#2563eb}}.bar{{height:8px;border-radius:999px;background:#e2e8f0;overflow:hidden;flex:1}}.bar span{{display:block;height:100%;width:{sc}%;border-radius:999px;background:linear-gradient(90deg,#60a5fa,#34d399)}}.feel{{background:linear-gradient(135deg,#ecfeff,#f0fdf4)}}.commute{{background:linear-gradient(135deg,#fff7ed,#fffbeb)}}.air{{background:linear-gradient(135deg,#f5f3ff,#eef2ff)}}.health{{background:linear-gradient(135deg,#f8fafc,#fefce8)}}.family{{background:linear-gradient(135deg,#eff6ff,#f8fafc)}}.food{{background:linear-gradient(135deg,#f0fdf4,#ecfdf5)}}.mystic{{background:linear-gradient(135deg,#faf5ff,#fdf2f8)}}.final{{display:flex;align-items:center;justify-content:center;min-height:112px;margin-top:12px;border-radius:24px;padding:22px 34px;text-align:center;color:#4b3528;background:linear-gradient(135deg,#fffaf0,#eefcff 52%,#f4fbf3);border:1px solid rgba(180,144,88,.20);box-shadow:0 12px 28px rgba(84,64,42,.08);font-family:var(--font-display);font-size:19px;font-weight:700;line-height:1.72;letter-spacing:.4px;text-wrap:balance}}.footer{{text-align:center;color:#94a3b8;font-size:12px;margin-top:12px}}
</style></head><body><div class="wrap"><div class="hero {th}"><div class="hero-top"><div class="city">{esc(d['city'])}</div><div class="badge">{esc(d['weather_desc'])} · {'夜间' if d['is_night'] else '白天'}</div></div><div class="date">{d['emoji']} {esc(d['target_date'])}｜{esc(lunar_line)}｜{now} 更新</div><div class="temp"><div class="temp-main">{d['temp']}°</div><div class="temp-sub">{esc(d['weather_desc'])}｜{d['min_temp']}–{d['max_temp']}℃<br>体感 {d['feels']}℃｜{esc(d['wind_desc'])}<br>空气{esc(d['aqi_label'])}｜降水 {d['precip_prob']}%</div></div><div class="summary">{esc(summary)}</div></div><div class="grid2"><div class="section"><div class="head"><div class="ico" style="background:#fff7cc">✨</div><div class="h">今日关键词</div></div><div class="chips">{kw}</div></div><div class="section"><div class="head"><div class="ico" style="background:#dbeafe">📊</div><div class="h">综合指数</div></div><div class="score"><div class="score-num">{sc}</div><div class="bar"><span></span></div></div><div class="body muted">适合轻量出行</div></div><div class="section feel"><div class="head"><div class="ico" style="background:#cffafe">🌡️</div><div class="h">天气体感</div></div><div class="body">{esc(d['weather_desc'])}｜{d['min_temp']}–{d['max_temp']}℃<br>体感 {d['feels']}℃<br><span class="muted">湿度 {d['humidity']}%，风速 {d['wind_speed']}km/h。</span></div></div><div class="section commute"><div class="head"><div class="ico" style="background:#fed7aa">🧥</div><div class="h">通勤穿搭</div></div><div class="body">{esc(d['cloth'])}<br>降水概率 {d['precip_prob']}%；{'带伞更稳。' if d['precip_prob']>40 else '正常出行即可。'}</div></div><div class="section air"><div class="head"><div class="ico" style="background:#ede9fe">🍃</div><div class="h">空气紫外线</div></div><div class="body">{aqi_title} {d['aqi'] or '—'}｜{esc(d['aqi_label'])}<br>UV {d['uv']}｜{esc(d['uv_level'])}<br><span class="muted">PM2.5 {d['pm25'] or '—'}</span></div></div><div class="section health"><div class="head"><div class="ico" style="background:#fef9c3">🏃</div><div class="h">健康活动</div></div><div class="body">适合：{esc(d['act_good'])}<br>不建议：{esc(d['act_bad'])}<br>运动后注意别吹风。</div></div><div class="section family"><div class="head"><div class="ico" style="background:#dbeafe">👨‍👩‍👧</div><div class="h">家庭提醒</div></div><div class="body">{esc(d.get('family_tip','按今日天气照顾家人出行与作息。'))}</div></div><div class="section food"><div class="head"><div class="ico" style="background:#dcfce7">🍵</div><div class="h">饮食建议</div></div><div class="body">{esc(d.get('food_tip','清淡均衡，多喝水。'))}</div></div><div class="section full mystic"><div class="head"><div class="ico" style="background:#f3e8ff">🧭</div><div class="h">宜忌参考 · 气象黄历</div></div><div class="body">{esc(d.get('almanac_tip','宜有序推进，忌拖延硬扛。')).replace('&lt;br&gt;', '<br>')}</div></div></div><div class="final">{esc(final_line_for(d))}</div><div class="footer">Lunar Weather｜Open-Meteo｜自动生成，仅供生活参考</div></div></body></html>"""


def browser_candidates():
    seen = set()
    for path in (
        os.environ.get("LUNAR_WEATHER_BROWSER"),
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        shutil.which("chromium"),
        shutil.which("google-chrome"),
        shutil.which("msedge"),
    ):
        if path and path not in seen and pathlib.Path(path).exists():
            seen.add(path)
            yield path


def render_with_browser(html_path, png_path):
    errors = []
    for browser in browser_candidates():
        with tempfile.TemporaryDirectory(prefix="lunar-weather-browser-") as profile:
            cmd = [
                browser,
                "--headless=new",
                "--disable-gpu",
                "--hide-scrollbars",
                "--no-sandbox",
                f"--user-data-dir={profile}",
                f"--screenshot={png_path}",
                "--window-size=1080,3600",
                html_path.as_uri(),
            ]
            try:
                proc = subprocess.run(cmd, text=True, capture_output=True, timeout=45)
            except Exception as e:
                errors.append({"browser": browser, "returncode": "exception", "detail": [str(e)]})
                continue
            if proc.returncode == 0 and png_path.exists() and png_path.stat().st_size > 1000:
                return True, errors
            detail = (proc.stderr or proc.stdout or "").strip().splitlines()[-3:]
            errors.append({"browser": browser, "returncode": proc.returncode, "detail": detail})
    return False, errors


def render_with_pillow(d, png_path):
    from PIL import Image, ImageDraw, ImageFont

    width = 1080
    margin = 54
    gap = 24
    content = width - margin * 2
    y = 40

    def load_font(path, size):
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            return ImageFont.load_default()

    fonts = {
        "title": load_font("/System/Library/Fonts/Supplemental/Songti.ttc", 78),
        "h1": load_font("/System/Library/Fonts/Supplemental/Songti.ttc", 42),
        "body": load_font("/System/Library/Fonts/STHeiti Light.ttc", 30),
        "bold": load_font("/System/Library/Fonts/STHeiti Medium.ttc", 30),
        "quote": load_font("/System/Library/Fonts/STHeiti Medium.ttc", 38),
        "small": load_font("/System/Library/Fonts/STHeiti Light.ttc", 25),
        "temp": load_font("/System/Library/Fonts/Supplemental/Georgia.ttf", 142),
    }

    def text_size(draw, text, font):
        box = draw.textbbox((0, 0), str(text), font=font)
        return box[2] - box[0], box[3] - box[1]

    def wrap(draw, text, font, max_width, max_lines=None):
        lines = []
        for para in str(text).replace("<br>", "\n").split("\n"):
            line = ""
            for ch in para.strip():
                trial = line + ch
                if text_size(draw, trial, font)[0] <= max_width or not line:
                    line = trial
                else:
                    lines.append(line)
                    line = ch
                    if max_lines and len(lines) >= max_lines:
                        last = lines[-1]
                        while text_size(draw, last + "…", font)[0] > max_width and last:
                            last = last[:-1]
                        lines[-1] = last + "…"
                        return lines
            if line:
                lines.append(line)
            if max_lines and len(lines) >= max_lines:
                return lines[:max_lines]
        return lines

    def draw_wrapped(draw, text, x, y, font, fill, max_width, line_gap=10, max_lines=None):
        for line in wrap(draw, text, font, max_width, max_lines):
            draw.text((x, y), line, font=font, fill=fill)
            y += text_size(draw, line or "口", font)[1] + line_gap
        return y

    def draw_wrapped_centered(draw, lines, box, font, fill, line_gap=10):
        x0, y0, x1, y1 = box
        line_heights = [text_size(draw, line or "口", font)[1] for line in lines]
        block_h = sum(line_heights) + max(0, len(lines) - 1) * line_gap
        y = y0 + max(0, (y1 - y0 - block_h) // 2)
        for line, line_h in zip(lines, line_heights):
            line_w = text_size(draw, line, font)[0]
            draw.text((x0 + max(0, (x1 - x0 - line_w) // 2), y), line, font=font, fill=fill)
            y += line_h + line_gap

    def rounded(draw, box, radius, fill, outline=None, width=1):
        draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)

    def vertical_gradient(draw, box, top, bottom):
        x0, y0, x1, y1 = box
        h = max(1, y1 - y0)
        for yy in range(y0, y1):
            t = (yy - y0) / h
            color = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
            draw.line((x0, yy, x1, yy), fill=color)

    img = Image.new("RGB", (width, 3600), "#eef5fb")
    draw = ImageDraw.Draw(img)
    vertical_gradient(draw, (0, 0, width, 3600), (238, 245, 251), (248, 253, 249))

    card = (40, 32, width - 40, 3560)
    rounded(draw, card, 48, "#f9fcff")

    hero = (margin, y, width - margin, y + 470)
    hero_img = Image.new("RGB", (hero[2] - hero[0], hero[3] - hero[1]), "#38bdf8")
    hero_draw = ImageDraw.Draw(hero_img)
    vertical_gradient(hero_draw, (0, 0, hero_img.width, hero_img.height), (56, 189, 248), (251, 191, 36))
    hero_mask = Image.new("L", hero_img.size, 0)
    ImageDraw.Draw(hero_mask).rounded_rectangle((0, 0, hero_img.width, hero_img.height), radius=40, fill=255)
    img.paste(hero_img, (hero[0], hero[1]), hero_mask)
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle(hero, radius=40, outline="#d8eefc", width=1)
    draw.text((hero[0] + 42, hero[1] + 44), d["city"], font=fonts["title"], fill="white")
    lunar = "｜".join(v for v in (d.get("lunar_date"), d.get("solar_term"), d.get("lunar_festival")) if v)
    draw.text((hero[0] + 44, hero[1] + 138), f"{d['target_date']}｜{lunar}｜{datetime.now().strftime('%H:%M')} 更新", font=fonts["small"], fill="white")
    draw.text((hero[0] + 42, hero[1] + 220), f"{d['temp']}°", font=fonts["temp"], fill="white")
    sub = f"{d['weather_desc']}｜{d['min_temp']}–{d['max_temp']}℃\n体感 {d['feels']}℃｜{d['wind_desc']}\n空气{d['aqi_label']}｜降水 {d['precip_prob']}%"
    sy = hero[1] + 248
    for line in sub.splitlines():
        draw.text((hero[0] + 310, sy), line, font=fonts["bold"], fill="white")
        sy += 50
    draw.rounded_rectangle((hero[0] + 36, hero[3] - 88, hero[2] - 36, hero[3] - 28), radius=28, fill="#eff8ff", outline="#d8eefc", width=2)
    draw_wrapped(draw, summary_for(d), hero[0] + 60, hero[3] - 76, fonts["bold"], "#334155", content - 120, 8, 2)
    y = hero[3] + gap

    sections = [
        ("今日关键词", "、".join(d["keywords"]), "#ffffff"),
        ("综合指数", f"{score(d)}｜适合轻量出行", "#f6fbff"),
        ("天气体感", f"{d['weather_desc']}｜{d['min_temp']}–{d['max_temp']}℃\n体感 {d['feels']}℃，湿度 {d['humidity']}%\n风速 {d['wind_speed']}km/h，{d['wind_desc']}。", "#ecfeff"),
        ("通勤穿搭", f"{d['cloth']}\n降水概率 {d['precip_prob']}%。{'带伞更稳。' if d['precip_prob'] > 40 else '正常出行即可。'}", "#fff7ed"),
        ("空气紫外线", f"{d.get('aqi_standard','AQI')} {d['aqi'] or '—'}｜{d['aqi_label']}\nPM2.5 {d['pm25'] or '—'}｜UV {d['uv']} {d['uv_level']}", "#f5f3ff"),
        ("健康活动", f"适合：{d['act_good']}\n不建议：{d['act_bad']}", "#f8fafc"),
        ("家庭提醒", d.get("family_tip", ""), "#eff6ff"),
        ("饮食建议", d.get("food_tip", ""), "#f0fdf4"),
    ]

    col_w = (content - gap) // 2
    for i in range(0, len(sections), 2):
        pair = sections[i:i + 2]
        heights = []
        for _, body, _ in pair:
            line_count = len(wrap(draw, body, fonts["body"], col_w - 56, 7))
            heights.append(max(190, 88 + line_count * 43))
        row_h = max(heights)
        for col, (title, body, fill) in enumerate(pair):
            x = margin + col * (col_w + gap)
            box = (x, y, x + col_w, y + row_h)
            rounded(draw, box, 28, fill, "#d8e2ee", 2)
            draw.text((x + 28, y + 24), title, font=fonts["h1"], fill="#4b3528")
            draw_wrapped(draw, body, x + 28, y + 82, fonts["body"], "#334155", col_w - 56, 10, 7)
        y += row_h + gap

    for title, body, fill, max_lines in [
        ("宜忌参考 · 气象黄历", d.get("almanac_tip", ""), "#fdf4ff", 8),
    ]:
        lines = wrap(draw, body, fonts["body"], content - 60, max_lines)
        h = max(170, 88 + len(lines) * 43)
        box = (margin, y, width - margin, y + h)
        rounded(draw, box, 30, fill, "#d8e2ee", 2)
        draw.text((margin + 30, y + 24), title, font=fonts["h1"], fill="#4b3528")
        draw_wrapped(draw, body, margin + 30, y + 82, fonts["body"], "#334155", content - 60, 10, max_lines)
        y += h + gap

    quote_lines = wrap(draw, final_line_for(d), fonts["quote"], content - 120, 3)
    quote_h = max(188, 92 + len(quote_lines) * 56)
    quote_box = (margin, y, width - margin, y + quote_h)
    rounded(draw, quote_box, 30, "#fffaf0", "#d8e2ee", 2)
    draw_wrapped_centered(draw, quote_lines, (margin + 60, y + 18, width - margin - 60, y + quote_h - 18), fonts["quote"], "#4b3528", 16)
    y += quote_h + gap

    footer = "Lunar Weather｜Open-Meteo｜自动生成，仅供生活参考"
    fw, _ = text_size(draw, footer, fonts["small"])
    draw.text(((width - fw) // 2, y), footer, font=fonts["small"], fill="#94a3b8")
    y += 60

    img.crop((0, 0, width, y + 28)).save(png_path)


def main():
    city = sys.argv[1] if len(sys.argv) > 1 else "上海"
    date = sys.argv[2] if len(sys.argv) > 2 else "today"
    data_proc = subprocess.run([sys.executable, str(DATA), city, date], text=True, capture_output=True)
    if data_proc.returncode != 0:
        msg = (data_proc.stderr or data_proc.stdout or "天气数据获取失败").strip()
        print(msg, file=sys.stderr)
        sys.exit(data_proc.returncode)
    raw = data_proc.stdout
    data = json.loads(raw)
    html_text = build_html(data)
    slug = f"weather-card-{data['city']}-{data['target_date']}"
    html_path = OUTDIR / f"{slug}.html"
    png_path = OUTDIR / f"{slug}.png"
    html_path.write_text(html_text, encoding="utf-8")

    render_errors = []
    if os.environ.get("LUNAR_WEATHER_RENDERER") == "browser":
        ok, render_errors = render_with_browser(html_path, png_path)
    else:
        ok = False

    renderer = "browser" if ok else "pillow"
    if renderer == "pillow":
        render_with_pillow(data, png_path)

    print(json.dumps({
        "html": str(html_path),
        "png": str(png_path),
        "renderer": renderer,
        "render_errors": render_errors[-3:],
        "data": data,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
