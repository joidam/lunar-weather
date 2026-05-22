#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render Lunar Weather card and prepare channel-safe delivery output.

Usage:
  python3 scripts/render_weather_delivery.py 上海 [today|YYYY-MM-DD] [--jpg]

Prints JSON with text, media path, and weather summary.
"""
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RENDER = ROOT / "scripts" / "render_weather_card.py"


def run(cmd):
    proc = subprocess.run(cmd, text=True, capture_output=True)
    if proc.returncode != 0:
        msg = (proc.stderr or proc.stdout or "命令执行失败").strip()
        raise RuntimeError(msg)
    return proc.stdout


def convert_to_jpeg(src, dest):
    try:
        from PIL import Image

        with Image.open(src) as im:
            im.convert("RGB").save(dest, "JPEG", quality=82, optimize=True)
        return
    except Exception:
        pass

    subprocess.check_call([
        "sips",
        "-s", "format", "jpeg",
        "-s", "formatOptions", "82",
        str(src),
        "--out", str(dest),
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main():
    city = sys.argv[1] if len(sys.argv) > 1 else "上海"
    date = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else "today"
    want_jpg = "--jpg" in sys.argv

    try:
        rendered = json.loads(run([sys.executable, str(RENDER), city, date]))
    except Exception as e:
        print(f"天气卡生成失败：{e}", file=sys.stderr)
        sys.exit(1)
    data = rendered["data"]
    media_path = pathlib.Path(rendered["png"])

    if want_jpg:
        jpg_path = media_path.with_name(media_path.stem + "-wechat.jpg")
        # WeChat has occasionally accepted uploads but not displayed large PNGs.
        convert_to_jpeg(media_path, jpg_path)
        media_path = jpg_path

    text = (
        f"Today's {data['city']} weather card is ready.\n"
        f"{data['weather_desc']}，{data['min_temp']}–{data['max_temp']}℃，"
        f"降水概率 {data['precip_prob']}%，AQI {data['aqi']}（{data['aqi_label']}）。"
    )
    print(json.dumps({
        "text": text,
        "media": str(media_path),
        "png": rendered["png"],
        "html": rendered["html"],
        "renderer": rendered.get("renderer"),
        "data": data,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
