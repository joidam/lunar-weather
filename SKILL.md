---
name: lunar-weather
description: >
  Generate localized daily weather reminder cards for chat apps (Feishu, WeChat/Weixin, etc.).
  Activates when user says "daily weather card", "weather reminder", "morning weather push", or "weather PNG".
  Uses Open-Meteo (free, no API key) to fetch live weather data and renders a mobile-friendly PNG card
  with dynamic weather themes and practical lifestyle sections.
---

# 🌙 Lunar Weather

Create polished daily weather cards for WeChat, Feishu/Lark, or any chat platform using live Open-Meteo data.

## What it does

- Fetches current weather, forecast, AQI, UV, wind, humidity, sunrise/sunset — no API key required.
- Renders a mobile-friendly card image via Microsoft Edge headless on macOS.
- Dynamically changes the card's header theme based on weather code + day/night.
- Includes practical sections: keywords, comfort score, alerts, outfit, air/UV, health activity, family tips, food suggestions, to-dos, and a quote.

## File map

- `scripts/get_weather_data.py` — fetch & normalize weather JSON from Open-Meteo.
- `scripts/render_weather_card.py` — render HTML → PNG via Edge headless.
- `assets/weather-card-template.html` — design reference template.
- `assets/lunar-weather-preview.png` — generic English preview.
- `assets/lunar-weather-preview-zh.png` — Chinese preview.

## Quick start

```bash
cd <your-workspace>/skills/lunar-weather

# Fetch weather for any city
python3 scripts/get_weather_data.py "Shanghai" today
python3 scripts/get_weather_data.py "Beijing" tomorrow

# Render card to PNG (outputs go to outputs/)
python3 scripts/render_weather_card.py "Shanghai" today
```

## Channel delivery

Replace target IDs with your own from OpenClaw channel config.

```bash
# WeChat / Weixin
openclaw message send \
  --channel openclaw-weixin \
  --target "<wechat-contact-id>" \
  --media outputs/weather-card-<City>-<date>.png \
  --message "🌙 Today's weather card"

# Feishu / Lark
openclaw message send \
  --channel feishu \
  --account "<account-id>" \
  --target "user:<open-id>" \
  --media outputs/weather-card-<City>-<date>.png \
  --message "🌙 Today's weather card"
```

## Weather → Theme mapping

| Weather code | Day theme | Night theme |
|---|---|---|
| 0–1 (clear) | sunny-day | sunny-night |
| 2–3 (cloudy) | cloudy-day | cloudy-night |
| 45, 48 (fog) | fog | fog |
| 51–67, 80–82 (rain) | rain-day | rain-night |
| 71–77, 85–86 (snow) | snow | snow |
| 95–99 (thunderstorm) | storm | storm |

## Notes

- **Edge headless** is used for deterministic HTML → PNG rendering on macOS.
- Keep personal delivery targets in OpenClaw config or cron jobs, not inside this skill.
- Open-Meteo is free and does not require an API key.
- This skill ships with city coordinates for common Chinese and international cities; you can add your own via the `CITY_COORDS` dict in `get_weather_data.py`.