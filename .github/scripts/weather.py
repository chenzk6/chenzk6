import urllib.request
import json
import datetime
import os

LAT, LON = 30.2741, 120.1551  # 杭州

WIDTH = 800

THEMES = {
    "light": {
        "bg": "#ffffff", "border": "#d0d7de",
        "title": "#24292f", "text": "#57606a", "muted": "#8b949e",
        "accent": "#2da44e",
    },
    "dark": {
        "bg": "#0d1117", "border": "#30363d",
        "title": "#e6edf3", "text": "#c9d1d9", "muted": "#8b949e",
        "accent": "#3fb950",
    },
}


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


def build_svg(data, theme):
    c = THEMES[theme]
    days = data["daily"]["time"]
    maxs = data["daily"]["temperature_2m_max"]
    mins = data["daily"]["temperature_2m_min"]
    wc = data["daily"]["weathercode"]

    svg = []
    svg.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="150" '
        f'viewBox="0 0 {WIDTH} 150" font-family="\'Segoe UI\', system-ui, sans-serif">'
    )
    svg.append(f'<rect x="0" y="0" width="{WIDTH}" height="150" rx="12" fill="{c["bg"]}"/>')
    svg.append(
        f'<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="149" rx="11.5" '
        f'fill="none" stroke="{c["border"]}" stroke-width="1"/>'
    )
    svg.append(
        f'<text x="28" y="34" font-size="14" font-weight="600" fill="{c["muted"]}">'
        f'<tspan fill="{c["accent"]}">&#9646;</tspan> 杭州天气 · Hangzhou · {datetime.date.today()}</text>'
    )

    step = (WIDTH - 56) / 7
    for i in range(min(7, len(days))):
        x = 28 + i * step + step / 2
        date_str = days[i][5:]  # MM-DD
        svg.append(f'<text x="{x:.1f}" y="66" font-size="12" fill="{c["muted"]}" text-anchor="middle">{date_str}</text>')
        svg.append(f'<text x="{x:.1f}" y="96" font-size="24" text-anchor="middle">{icon_for(wc[i])}</text>')
        svg.append(
            f'<text x="{x:.1f}" y="124" font-size="13" fill="{c["text"]}" text-anchor="middle">'
            f'{int(mins[i])}° / {int(maxs[i])}°</text>'
        )

    svg.append("</svg>")
    return "\n".join(svg)


def main():
    data = fetch_forecast()
    os.makedirs("assets", exist_ok=True)
    for theme in ("light", "dark"):
        suffix = "-dark" if theme == "dark" else ""
        content = build_svg(data, theme)
        with open(f"assets/weather{suffix}.svg", "w", encoding="utf-8") as f:
            f.write(content)
        print(f"weather{suffix}.svg generated")


if __name__ == "__main__":
    main()
