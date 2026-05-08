# 🌙 Lunar Weather

> Generate polished daily weather reminder cards for WeChat, Feishu/Lark, and any chat platform — no API key required, powered by Open-Meteo.

![Weather Card Preview](assets/lunar-weather-preview.png)

## ✨ Features

- **Zero-config weather data** — Live data from [Open-Meteo](https://open-meteo.com/) (completely free, no API key)
- **Dynamic card themes** — Header color/style automatically adapts to weather condition + day/night state
  - ☀️ Sunny day/night, ☁️ Cloudy, 🌫️ Fog, 🌧️ Rain, ❄️ Snow, ⛈️ Storm
- **Mobile-optimized PNG output** — Renders via Microsoft Edge headless for pixel-perfect consistency
- **Rich lifestyle sections** — Keywords, comfort score, alerts, outfit, air quality, UV index, health tips, family notes, food suggestions, daily to-dos, and an inspirational quote
- **Multi-channel delivery** — Works with WeChat, Feishu/Lark, and any OpenClaw-connected platform
- **Cron-ready** — Designed for daily 08:00 automated pushes via OpenClaw cron jobs

## 🚀 Quick Start

### 1. Install

```bash
cd ~/.openclaw/workspace/skills
git clone https://github.com/joidam/lunar-weather.git
```

### 2. Get weather data

```bash
cd lunar-weather
python3 scripts/get_weather_data.py "Shanghai" today
python3 scripts/get_weather_data.py "Beijing" tomorrow
```

Supported city formats: `Shanghai`, `北京`, `Tokyo`, `London`, etc. (uses built-in coordinates for common cities; falls back to Nominatim geocoding for others).

### 3. Render card to PNG

```bash
python3 scripts/render_weather_card.py "Shanghai" today
# Output: outputs/weather-card-Shanghai-2026-05-08.png
```

### 4. Deliver via OpenClaw

```bash
# WeChat / Weixin
openclaw message send \
  --channel openclaw-weixin \
  --target "<your-contact-id>" \
  --media outputs/weather-card-Shanghai-2026-05-08.png \
  --message "🌙 Today's weather — May 8"

# Feishu / Lark
openclaw message send \
  --channel feishu \
  --account main \
  --target "user:<open-id>" \
  --media outputs/weather-card-Shanghai-2026-05-08.png \
  --message "🌙 Today's weather — May 8"
```

## 🧩 Card Sections

| Section | Description |
|---|---|
| 🌤️ Hero | City, date/time, temperature, feels-like, weather summary |
| ✨ Keywords | 3 tags derived from weather, wind, and air quality |
| 📊 Comfort Score | Single 0–100 score based on precipitation, AQI, and temperature |
| 🚨 Alert | Weather warning if applicable (none if clear) |
| 🌡️ Feels Like | Temperature range, apparent temp, humidity, wind speed |
| 🧥 Outfit | Temperature-based clothing recommendation |
| 🍃 Air & UV | AQI level + label, UV index, PM2.5 |
| 🏃 Health & Activity | Recommended / discouraged activities for current conditions |
| 👨‍👩‍👧 Family Tips | Elderly and children care reminders |
| 🍵 Food & Drink | Dietary suggestions (warm drinks, avoid iced) |
| 🧭 To-Do / Avoid | Daily recommendations and things to skip |
| 💡 One-liner + Quote | Actionable advice + aligned daily quote |

## 🎨 Theme Mapping

| Weather Code | Condition | Day Theme | Night Theme |
|---|---|---|---|
| 0–1 | Clear / Few clouds | ☀️ Sunny blue-gold | 🌙 Deep blue + violet |
| 2–3 | Cloudy / Overcast | ⛅ Gray-blue cloud | ☁️ Dark slate blue |
| 45, 48 | Fog | 🌫️ Muted gray-white | 🌫️ Same |
| 51–67, 80–82 | Rain / Drizzle | 🌧️ Blue-gray rain | 🌧️ Deep blue-gray |
| 71–77, 85–86 | Snow | ❄️ Ice blue-white | ❄️ Same |
| 95–99 | Thunderstorm | ⛈️ Purple-black + yellow | ⛈️ Same |

## 🛠️ Requirements

- **macOS** (Edge headless is used for HTML → PNG rendering)
- **Microsoft Edge** installed
- **Python 3.10+**
- **OpenClaw** with WeChat/Feishu channel configured
- **Open-Meteo** — no API key, no account needed

## 📁 File Structure

```
lunar-weather/
├── SKILL.md                          # OpenClaw skill definition
├── README.md                         # This file
├── scripts/
│   ├── get_weather_data.py           # Fetch & normalize weather from Open-Meteo
│   └── render_weather_card.py        # Render HTML template → PNG via Edge
└── assets/
    ├── weather-card-template.html    # Design reference template
    └── lunar-weather-preview.png     # Preview screenshot
```

## 🤝 Contributing

Pull requests welcome! For major changes, please open an issue first.

## 📄 License

MIT — use freely, no strings attached.
