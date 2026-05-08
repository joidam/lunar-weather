---
name: lunar-weather
description: >
  生成本地化每日天气推送卡（支持飞书/微信）。当用户说“每天天气推送”“天气提醒”“生成今日天气卡片”
  或主动触发每日定时任务时激活。
  基于 Open-Meteo 实时数据，渲染手机端友好的天气长图（PNG）发微信，
  或飞书交互卡片消息。无需 API key。
---

# 🌙 Lunar Weather

An OpenClaw skill for generating localized daily weather cards.

## Features

- Queries Open-Meteo for real-time + forecast weather data (no API key required)
- Renders a mobile-friendly PNG weather card with dynamic themes
- Supports WeChat (PNG image) and Feishu (interactive card)
- Configurable daily cron push

## Weather Theme Mapping

Top hero background auto-matches `weather_code + day/night`:

| Weather | Day | Night |
|---------|-----|-------|
| Clear 0-1 | sunny-day | sunny-night |
| Cloudy 2-3 | cloudy-day | cloudy-night |
| Fog 45/48 | fog | fog |
| Rain 51-67/80-82 | rain-day | rain-night |
| Snow 71-77/85-86 | snow | snow |
| Storm 95-99 | storm | storm |

## Workflow

### Step 1: Get weather data

```bash
python3 scripts/get_weather_data.py <City> [YYYY-MM-DD]
```

### Step 2: Render weather card PNG

```bash
python3 scripts/render_weather_card.py <City> [YYYY-MM-DD]
```

- Calls `get_weather_data.py` to fetch real data
- Reads `assets/weather-card-template.html` and fills in live data
- Renders via Edge headless → PNG output
- Output: `outputs/weather-card-<City>-<Date>.png`

### Step 3: Push

**WeChat**: `openclaw message send --channel openclaw-weixin -t <to> --media <png>`
**Feishu**: `openclaw message send --channel feishu -t <to> --json <card>`

## Quick Test

```bash
python3 scripts/get_weather_data.py Beijing
python3 scripts/render_weather_card.py Beijing
ls -lh outputs/
```

## Key Files

- `assets/weather-card-template.html` — Card HTML template
- `scripts/get_weather_data.py` — Open-Meteo data fetch
- `scripts/render_weather_card.py` — PNG renderer
- `SKILL.md` — This file

## Design Notes

- Typography: Georgia serif for headlines, system sans for body
- Dynamic hero theme based on weather + time-of-day
- All sections: keywords, score, alerts, feels-like, outfit, UV/AQ, health, family, food, to-dos, quote
- Bottom one-line advice in soft warm tones
