import urllib.request
import json
import datetime
import os

LAT, LON = 30.2741, 120.1551  # 杭州

def fetch_forecast():
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={LAT}&longitude={LON}"
        f"&daily=weathercode,temperature_2m_max,temperature_2m_min"
        f"&timezone=Asia%2FShanghai&forecast_days=7"
    )
    with urllib.request.urlopen(url) as resp:
        return json.load(resp)

def icon_for(code):
    return {
        0: "☀️", 1: "🌤", 2: "⛅️", 3: "☁️",
        45: "🌫", 48: "🌫",
        61: "🌧", 63: "🌧", 65: "🌧",
        71: "❄️", 73: "❄️", 75: "❄️",
        95: "⛈", 96: "⛈", 99: "⛈",
    }.get(code, "🌡")

def build_svg(data):
    days = data["daily"]["time"]
    maxs = data["daily"]["temperature_2m_max"]
    mins = data["daily"]["temperature_2m_min"]
    wc = data["daily"]["weathercode"]

    svg = []
    svg.append('<svg xmlns="http://www.w3.org/2000/svg" width="480" height="140">')
    svg.append(f'<rect width="480" height="140" rx="12" fill="#0d1117"/>')
    svg.append(f'<text x="20" y="28" font-size="16" fill="#58a6ff">杭州天气 {datetime.date.today()}</text>')

    for i in range(min(7, len(days))):
        x = 20 + i * 66
        date_str = days[i][5:]  # MM-DD
        svg.append(f'<text x="{x}" y="56" font-size="12" fill="#c9d1d9">{date_str}</text>')
        svg.append(f'<text x="{x}" y="82" font-size="20">{icon_for(wc[i])}</text>')
        svg.append(
            f'<text x="{x}" y="108" font-size="12" fill="#c9d1d9">'
            f'{int(mins[i])}°/{int(maxs[i])}°</text>'
        )

    svg.append("</svg>")
    return "\n".join(svg)

def main():
    data = fetch_forecast()
    content = build_svg(data)
    os.makedirs("output", exist_ok=True)  # 生成到 output/ 子目录
    with open("output/weather.svg", "w", encoding="utf-8") as f:
        f.write(content)
    print("weather.svg generated")

if __name__ == "__main__":
    main()
