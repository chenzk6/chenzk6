import urllib.request, json, datetime
LAT, LON = 30.2741, 120.1551
url = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&daily=weathercode,temperature_2m_max,temperature_2m_min&timezone=Asia%2FShanghai&forecast_days=7"
data = json.load(urllib.request.urlopen(url))
days = data["daily"]["time"]
maxs = data["daily"]["temperature_2m_max"]
mins = data["daily"]["temperature_2m_min"]
wc = data["daily"]["weathercode"]

def icon(c):
    return {0:"☀️",1:"🌤",2:"⛅️",3:"☁️",61:"🌧",71:"❄️",95:"⛈"}.get(c,"🌡")

svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="420" height="120">']
svg.append(f'<text x="10" y="24" font-size="16">杭州天气 {datetime.date.today()}</text>')
for i in range(7):
    x = 10 + i*60
    svg.append(f'<text x="{x}" y="50" font-size="12">{days[i][5:]}</text>')
    svg.append(f'<text x="{x}" y="74" font-size="18">{icon(wc[i])}</text>')
    svg.append(f'<text x="{x}" y="96" font-size="12">{int(mins[i])}°/{int(maxs[i])}°</text>')
svg.append('</svg>')
open("output/weather.svg","w",encoding="utf-8").write("\n".join(svg))
