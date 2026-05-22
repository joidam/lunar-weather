---
name: lunar-weather
description: >
  Generate localized daily weather + lifestyle almanac cards for WeChat, Feishu/Lark,
  and OpenClaw cron delivery. Uses Open-Meteo live data, lunar/solar-term context,
  dynamic weather themes, and optional JPG compression. No API key required.
---

# 🌙 Lunar Weather

An OpenClaw skill for generating polished daily weather cards with lightweight lifestyle almanac guidance.

## Features

- Queries Open-Meteo for real-time + forecast weather data (no API key required)
- Renders a mobile-friendly PNG card with dynamic weather themes
- Uses stable Pillow rendering by default with optional browser screenshot debugging
- Adds dynamic lunar date, solar term/festival, Gan-Zhi, Bagua, astrology, and Huangji-style symbolic context
- Generates data-driven family reminders, food suggestions, and health/activity advice
- Keeps alerts compact: normal days hide alert panels; meaningful warnings appear in keyword chips
- Supports optional JPG compression for WeChat-style delivery
- Rejects unsupported cities, past dates, and forecast dates outside Open-Meteo's public window
- Designed for daily cron pushes via OpenClaw

> Almanac/astrology/Bagua/Huangji-style content is a lifestyle reference layer, not deterministic prediction or professional advice.

## Workflow

### Step 1: Get weather data

```bash
python3 scripts/get_weather_data.py <City> [today|tomorrow|YYYY-MM-DD]
```

### Step 2: Render weather card PNG

```bash
python3 scripts/render_weather_card.py <City> [today|tomorrow|YYYY-MM-DD]
```

### Step 3: Prepare delivery payload

```bash
python3 scripts/render_weather_delivery.py <City> today
python3 scripts/render_weather_delivery.py <City> today --jpg
```

The delivery helper prints JSON with:

- `text` — short summary/caption
- `media` — final media path for delivery
- `png` — original PNG path
- `html` — rendered HTML path

### Step 4: Deliver with OpenClaw

Return text plus a `MEDIA:` directive:

```text
<text>
MEDIA:<media-path>
```

## Key Files

- `scripts/get_weather_data.py` — Open-Meteo data + lunar/almanac context
- `scripts/render_weather_card.py` — card renderer → PNG via Pillow, with optional browser screenshot mode
- `scripts/render_weather_delivery.py` — delivery JSON + optional JPG compression
- `assets/lunar-weather-preview.png` — public privacy-safe preview
- `SKILL.md` — this file

## Design Notes

- Typography: display serif for headings, system sans for body
- Dynamic hero theme based on weather + day/night
- Full-width “Weather Almanac” section replaces repetitive to-dos
- Alert chip appears only when there is a meaningful weather warning
- Centered quote footer avoids repeating the hero weather summary
