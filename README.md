# 🌙 Lunar Weather

> Generate polished daily weather + almanac cards for WeChat, Feishu/Lark, and any chat platform — no API key required, powered by Open-Meteo.

![Weather Card Preview](assets/lunar-weather-preview.png)

## ✨ What's New

- **Compact alert design** — normal days no longer waste a full warning panel; real alerts are merged into the keyword chips.
- **Dynamic weather almanac** — combines weather, lunar date, solar terms, heavenly stems/earthly branches, Bagua, light astrology, and a Huangji-style symbolic index.
- **Smarter lifestyle guidance** — family reminders, food suggestions, and health/activity tips now change with both weather conditions and daily symbolic context.
- **Full-width “Weather Almanac” block** — replaces the old repetitive daily to-do panel with a richer horizontal almanac section.
- **WeChat-friendly delivery helper** — optional compressed JPG output for channels that may silently drop large PNGs.

## ✨ Features

- **Zero-config weather data** — Live data from [Open-Meteo](https://open-meteo.com/) (free, no API key)
- **Dynamic card themes** — Header color/style adapts to weather condition + day/night state
  - ☀️ Sunny day/night, ☁️ Cloudy, 🌫️ Fog, 🌧️ Rain, ❄️ Snow, ⛈️ Storm
- **Mobile-optimized output** — Renders via Microsoft Edge headless for pixel-perfect PNG cards
- **Weather + lifestyle sections** — Keywords, comfort score, feels-like, outfit, air quality, UV index, health tips, family notes, food suggestions, weather almanac, and quote
- **Alert-aware layout** — Warning chip appears only when meaningful weather alerts exist
- **Multi-channel delivery** — Works with WeChat, Feishu/Lark, and any OpenClaw-connected platform
- **Cron-ready** — Designed for daily automated pushes via OpenClaw cron jobs

> Note: lunar/almanac/astrology/Bagua/Huangji-style fields are lightweight lifestyle references, not deterministic predictions or professional advice.

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

### 3. Render card to PNG

```bash
python3 scripts/render_weather_card.py "Shanghai" today
# Output: outputs/weather-card-Shanghai-YYYY-MM-DD.png
```

### 4. Prepare delivery payload

```bash
# PNG for most channels
python3 scripts/render_weather_delivery.py "Shanghai" today

# Smaller JPG for WeChat-style channels
python3 scripts/render_weather_delivery.py "Shanghai" today --jpg
```

The delivery helper prints JSON:

```json
{
  "text": "...short weather summary...",
  "media": "...image path...",
  "png": "...png path..."
}
```

### 5. OpenClaw `MEDIA:` delivery pattern

For OpenClaw agent/cron delivery, use the returned `text` and `media`:

```text
<text>
MEDIA:<media-path>
```

## 🧩 Card Sections

| Section | Description |
|---|---|
| 🌤️ Hero | City, date/time, lunar date, temperature, feels-like, weather summary |
| ✨ Keywords | Weather, wind, AQI tags; meaningful alerts appear here as red chips |
| 📊 Comfort Score | Single 0–100 score based on precipitation, AQI, and temperature |
| 🌡️ Feels Like | Temperature range, apparent temp, humidity, wind speed |
| 🧥 Outfit | Temperature-based clothing recommendation |
| 🍃 Air & UV | AQI level + label, UV index, PM2.5 |
| 🏃 Health & Activity | Recommended / discouraged activities from weather + symbolic context |
| 👨‍👩‍👧 Family Tips | Weather safety guidance adjusted by lunar/Bagua/astrology context |
| 🍵 Food & Drink | Dietary suggestions based on heat/cold/rain/AQI + seasonal context |
| 🧭 Weather Almanac | Full-width dynamic almanac: lunar date, solar term/festival, Gan-Zhi, Bagua, astrology, Huangji-style symbolic index |
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

- **macOS** (Microsoft Edge headless is used for HTML → image rendering)
- **Microsoft Edge** installed at `/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge`
- **Python 3.10+**
- **Open-Meteo** — no API key, no account needed
- Optional: **OpenClaw** with WeChat/Feishu channel configured for automated delivery

## 📁 File Structure

```text
lunar-weather/
├── SKILL.md
├── README.md
├── scripts/
│   ├── get_weather_data.py           # Fetch + normalize weather, lunar, almanac context
│   ├── render_weather_card.py        # Render HTML → PNG via Edge
│   └── render_weather_delivery.py    # Prepare text + media JSON, optional JPG compression
└── assets/
    ├── weather-card-template.html
    └── lunar-weather-preview.png
```

## 🔒 Privacy Notes

- The preview image uses a generic sample city.
- Do not commit private chat IDs, OpenClaw account IDs, local usernames, or exact personal locations.
- For public examples, prefer generic cities and placeholder delivery targets.

## 🤝 Contributing

Pull requests welcome! For major changes, please open an issue first.

## 📄 License

MIT — use freely, no strings attached.
