# 🌙 Lunar Weather

> Generate polished daily weather + almanac cards for WeChat, Feishu/Lark, and any chat platform — no API key required, powered by Open-Meteo.

![Weather Card Preview](assets/lunar-weather-preview.png)

## ✨ What's New

- **Richer “今日小句” footer** — Weather, temperature, AQI, solar terms, weekends, and month boundaries now shape the closing line.
- **Repeat guard** — Local quote history avoids recent repeats while keeping the same city/date render stable.
- **Stable default renderer** — Pillow is the default PNG renderer; browser screenshots remain available for debugging with `LUNAR_WEATHER_RENDERER=browser`.
- **More resilient Open-Meteo fetches** — weather requests retry with stepped timeouts before failing clearly.
- **Safer forecast handling** — unsupported cities, past dates, and dates beyond the forecast window now fail explicitly.
- **Delivery helper upgrades** — JSON output reports the renderer and JPEG conversion can use Pillow before falling back to macOS `sips`.

## ✨ Features

- **Zero-config weather data** — Live data from [Open-Meteo](https://open-meteo.com/) (free, no API key)
- **Dynamic card themes** — Header color/style adapts to weather condition + day/night state
  - ☀️ Sunny day/night, ☁️ Cloudy, 🌫️ Fog, 🌧️ Rain, ❄️ Snow, ⛈️ Storm
- **Mobile-optimized output** — Renders stable Pillow PNG cards by default, with optional browser screenshot rendering for debugging
- **Weather + lifestyle sections** — Keywords, comfort score, feels-like, outfit, air quality, UV index, health tips, family notes, food suggestions, weather almanac, and daily line
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
| 💡 Daily Line | Centered weather-aligned “今日小句” with recent-repeat protection |

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

- **Python 3.10+**
- **Pillow** for stable PNG/JPG rendering
- Optional: **Microsoft Edge**, **Google Chrome**, or Chromium for browser screenshot debugging
- **Open-Meteo** — no API key, no account needed
- Optional: **OpenClaw** with WeChat/Feishu channel configured for automated delivery

## 📁 File Structure

```text
lunar-weather/
├── SKILL.md
├── README.md
├── scripts/
│   ├── get_weather_data.py           # Fetch + normalize weather, lunar, almanac context
│   ├── render_weather_card.py        # Render card to PNG via Pillow / optional browser
│   └── render_weather_delivery.py    # Prepare text + media JSON, optional JPG compression
└── assets/
    ├── weather-card-template.html
    └── lunar-weather-preview.png
```

## 🔒 Privacy Notes

- Preview images use generic sample cities and include no exact personal location.
- Do not commit private chat IDs, OpenClaw account IDs, local usernames, or exact personal locations.
- For public examples, prefer generic cities and placeholder delivery targets.

## 🤝 Contributing

Pull requests welcome! For major changes, please open an issue first.

## 📄 License

MIT — use freely, no strings attached.
