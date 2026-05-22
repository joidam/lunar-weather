# Changelog

## v1.2.0 — Stable Renderer + Quote Footer

- Replaced the repetitive one-liner footer with a centered weather-aligned daily quote.
- Added a stable Pillow-based PNG renderer as the default path while keeping optional browser screenshot mode for debugging.
- Added stepped Open-Meteo retries and clearer failures for request, render, and delivery-helper errors.
- Added strict city/date validation for unsupported cities, historical dates, and forecasts beyond the public forecast window.
- Improved future-day forecast selection, AQI labeling, and delivery-helper JPEG conversion fallback behavior.
- Refreshed the public preview card with a new privacy-safe sample image.

## v1.1.0 — Dynamic Weather Almanac

- Added dynamic lunar/almanac context: lunar date, solar terms, traditional festivals, Gan-Zhi day, Bagua, light astrology, and Huangji-style symbolic index.
- Family reminders, food advice, and health/activity tips now vary with weather + daily symbolic context.
- Replaced the old repetitive daily to-do panel with a full-width “Weather Almanac” section.
- Merged meaningful alerts into keyword chips; normal days no longer show an empty warning panel.
- Added `scripts/render_weather_delivery.py` for delivery-friendly JSON output and optional WeChat-friendly JPG compression.
- Updated preview images with privacy-safe generic sample cities, including a full-English card.

## v1.0.0

- Initial public release: Open-Meteo weather fetcher, dynamic card themes, Edge-based PNG rendering, and mobile-friendly weather card layout.
