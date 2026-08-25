#!/usr/bin/env python3
"""Generate self-hosted SVG cards for the GitHub profile README.

Produces, into assets/ (light + dark variants):
  banner, typing, journey, projects, clock

journey/projects/clock pull data from the GitHub REST API. When the
GITHUB_TOKEN env var is set it is used for a higher rate limit; without it
the script still works at unauthenticated limits for a single run.
"""
import json
import os
import urllib.request
from datetime import datetime, timedelta, timezone

# ---------------------------------------------------------------------------
# 配置：改成你自己的信息
# ---------------------------------------------------------------------------
USERNAME = "chenzk6"
TAGLINE = "Embodied AI · Robot Learning · LLM Agent"
TYPING_LINES = [
    "Embodied AI · Robot Learning · LLM Agent",
    "Building embodied agents that think & act",
]
# TODO: 填入真实链接，留空字符串则不显示对应项
LINKS = {
    "email": "czk2929337684@163.com",      # 例: "you@example.com"
    # "scholar": "",    # 例: "https://scholar.google.com/citations?user=XXXX"
    "website": "https://chenzk6.github.io/",    # 例: "https://your-site.com"
}
# 可选：固定展示的仓库名（按此顺序），留空则自动按 star/更新时间选 top4
PINNED_REPOS = ["robonix", "xiuos"]  # 想展示更多就追加，如 ["robonix", "xiuos", "MVS"]

# ---------------------------------------------------------------------------
# 主题（浅绿 accent）
# ---------------------------------------------------------------------------
THEMES = {
    "light": {
        "bg": "#ffffff", "border": "#d0d7de",
        "title": "#24292f", "text": "#57606a", "muted": "#8b949e",
        "accent": "#2da44e", "accent_soft": "#dafbe1",
    },
    "dark": {
        "bg": "#0d1117", "border": "#30363d",
        "title": "#e6edf3", "text": "#c9d1d9", "muted": "#8b949e",
        "accent": "#3fb950", "accent_soft": "#12361f",
    },
}

SANS = "'Segoe UI', system-ui, -apple-system, Helvetica, Arial, sans-serif"
MONO = "'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace"

WIDTH = 800
CST = timezone(timedelta(hours=8))  # Asia/Shanghai

LANG_COLORS = {
    "Python": "#3572A5", "C++": "#f34b7d", "C": "#555555",
    "Rust": "#dea584", "Go": "#00ADD8", "JavaScript": "#f1e05a",
    "TypeScript": "#3178c6", "Java": "#b07219", "Jupyter Notebook": "#DA5B0B",
    "Shell": "#89e051", "HTML": "#e34c26", "CSS": "#563d7c",
    "MATLAB": "#e16737", "CMake": "#DA3434",
}


def esc(s):
    return (
        str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        .replace('"', "&quot;").replace("'", "&#39;")
    )


def gh(path):
    url = "https://api.github.com" + path
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "chenzk6-readme-generator",
    }
    token = os.environ.get("GITHUB_TOKEN", "")
    if token:
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def svg_doc(theme, height, inner):
    c = THEMES[theme]
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" '
        f'viewBox="0 0 {WIDTH} {height}" font-family="{SANS}">\n'
        f'  <rect x="0" y="0" width="{WIDTH}" height="{height}" rx="12" fill="{c["bg"]}"/>\n'
        f"{inner}\n</svg>"
    )


def section_title(theme, y, title):
    c = THEMES[theme]
    return (
        f'<text x="28" y="{y}" font-size="14" font-weight="600" fill="{c["muted"]}">'
        f'<tspan fill="{c["accent"]}">&#9646;</tspan> {esc(title)}</text>'
    )


# ---------------------------------------------------------------------------
# Banner
# ---------------------------------------------------------------------------
def _host(url):
    return url.replace("https://", "").replace("http://", "").rstrip("/")


def build_banner(theme):
    c = THEMES[theme]
    link_items = [f"github.com/{USERNAME}"]
    if LINKS.get("email"):
        link_items.append(LINKS["email"])
    if LINKS.get("scholar"):
        link_items.append("Google Scholar")
    if LINKS.get("website"):
        link_items.append(_host(LINKS["website"]))
    link_text = "  ·  ".join(esc(x) for x in link_items)

    inner = "\n".join([
        f'  <rect x="28" y="30" width="6" height="104" rx="3" fill="{c["accent"]}"/>',
        f'  <text x="52" y="66" font-size="30" font-weight="700" fill="{c["title"]}">'
        f'<tspan>Chen Zikun</tspan> '
        f'<tspan fill="{c["muted"]}" font-weight="400">· 陈子坤</tspan></text>',
        f'  <text x="52" y="96" font-size="16" fill="{c["text"]}">{esc(TAGLINE)}</text>',
        f'  <text x="52" y="124" font-size="13" font-family="{MONO}" fill="{c["accent"]}">{link_text}</text>',
    ])
    return svg_doc(theme, 158, inner)


# ---------------------------------------------------------------------------
# Typing
# ---------------------------------------------------------------------------
def build_typing(theme):
    c = THEMES[theme]
    # Typewriter: each character pops in one at a time (discrete steps) like
    # real keyboard input, then the phrase is erased and the next one typed.
    # Every char is its own <tspan> with a discrete opacity step, so the font
    # handles spacing (no fixed char-width assumption). A cursor jumps with the
    # typing and blinks on its own 1s loop.
    if not TYPING_LINES:
        return svg_doc(theme, 92, "")

    char_w = 11       # monospace advance at font-size 20 (cursor tracking only)
    dur = 14          # seconds per full loop

    def type_t(p, i, n):
        s = 0.02 if p == 0 else 0.50
        e = 0.32 if p == 0 else 0.80
        return s if n <= 1 else s + (e - s) * i / (n - 1)

    def erase_t(p, i, n):
        # backspace: rightmost char vanishes first
        s = 0.44 if p == 0 else 0.92
        e = 0.47 if p == 0 else 0.95
        return s if n <= 1 else s + (e - s) * (n - 1 - i) / (n - 1)

    texts = []
    cursor_events = [(0.0, 28.0), (1.0, 28.0)]

    for p, phrase in enumerate(TYPING_LINES):
        n = len(phrase)
        spans = []
        for i, ch in enumerate(phrase):
            a = type_t(p, i, n)
            b = erase_t(p, i, n)
            glyph = "&#160;" if ch == " " else esc(ch)
            spans.append(
                f'<tspan>{glyph}'
                f'<animate attributeName="opacity" values="0; 1; 0; 0" '
                f'keyTimes="0; {a:.4f}; {b:.4f}; 1" calcMode="discrete" '
                f'dur="{dur}s" repeatCount="indefinite"/></tspan>'
            )
            cursor_events.append((a, 28.0 + (i + 1) * char_w))
            cursor_events.append((b, 28.0 + i * char_w))
        texts.append(
            f'  <text x="28" y="52" font-size="20" font-family="{MONO}" '
            f'fill="{c["title"]}">{"".join(spans)}</text>'
        )

    cursor_events.sort()
    times = [t for t, _ in cursor_events]
    xs = [x for _, x in cursor_events]
    cursor = (
        f'  <text y="52" font-size="20" font-family="{MONO}" fill="{c["accent"]}">|'
        f'<animateTransform attributeName="transform" type="translate" '
        f'values="{"; ".join(f"{x:.0f} 0" for x in xs)}" '
        f'keyTimes="{"; ".join(f"{t:.4f}" for t in times)}" calcMode="discrete" '
        f'dur="{dur}s" repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values="1; 1; 0; 0; 1; 1" '
        f'keyTimes="0; 0.5; 0.6; 0.7; 0.9; 1" dur="1s" repeatCount="indefinite"/></text>'
    )

    return svg_doc(theme, 92, "\n".join(texts + [cursor]))


# ---------------------------------------------------------------------------
# Journey
# ---------------------------------------------------------------------------
def recent_activity(events):
    if not isinstance(events, list):
        return 0
    cutoff = datetime.now(timezone.utc) - timedelta(days=30)
    active = {"PushEvent", "PullRequestEvent", "IssuesEvent",
              "CreateEvent", "PullRequestReviewEvent"}
    n = 0
    for e in events:
        if e.get("type") in active:
            try:
                dt = datetime.fromisoformat(e["created_at"].replace("Z", "+00:00"))
            except Exception:
                continue
            if dt >= cutoff:
                n += 1
    return n


def build_journey(theme, user, events):
    c = THEMES[theme]
    joined = str(user.get("created_at", ""))[:4] or "—"
    repos_n = user.get("public_repos", 0)
    recent = recent_activity(events)

    metrics = [
        (joined, "Joined"),
        (str(repos_n), "Public repos"),
        (str(recent), "Events · last 30d"),
    ]
    cols = []
    for i, (value, label) in enumerate(metrics):
        x = 400 + (i - 1) * 267
        cols.append(
            f'  <text x="{x}" y="82" text-anchor="middle" font-size="30" '
            f'font-weight="700" font-family="{MONO}" fill="{c["accent"]}">{esc(value)}</text>'
        )
        cols.append(
            f'  <text x="{x}" y="108" text-anchor="middle" font-size="13" '
            f'fill="{c["muted"]}">{esc(label)}</text>'
        )
    inner = section_title(theme, 38, "Journey") + "\n" + "\n".join(cols)
    return svg_doc(theme, 134, inner)


# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------
def _pick_repos(repos):
    if not isinstance(repos, list):
        return []
    eligible = [
        r for r in repos
        if not r.get("archived")
        and r.get("name") != USERNAME
        and r.get("name") != f"{USERNAME}.github.io"
    ]
    if PINNED_REPOS:
        by_name = {r.get("name"): r for r in eligible}
        return [by_name[n] for n in PINNED_REPOS if n in by_name]
    # 自动模式排除 fork；star 优先，star 相同时按最近 push 排序
    own = [r for r in eligible if not r.get("fork")]
    own.sort(key=lambda r: (r.get("stargazers_count", 0), r.get("pushed_at") or ""), reverse=True)
    return own[:4]


def build_projects(theme, repos):
    c = THEMES[theme]
    picked = _pick_repos(repos)
    inner = [section_title(theme, 38, "Projects")]

    if not picked:
        inner.append(
            f'  <text x="28" y="80" font-size="15" fill="{c["muted"]}">'
            'No public repositories yet.</text>'
        )
        return svg_doc(theme, 118, "\n".join(inner))

    y = 72
    for r in picked:
        name = r.get("name", "untitled")
        desc = (r.get("description") or "").strip()
        if len(desc) > 88:
            desc = desc[:87].rstrip() + "…"
        lang = r.get("language")
        stars = r.get("stargazers_count", 0)
        fork_mark = (
            f' <tspan fill="{c["muted"]}" font-weight="400" font-size="12">· fork</tspan>'
            if r.get("fork") else ""
        )

        inner.append(
            f'  <text x="28" y="{y}" font-size="16" font-weight="700" '
            f'font-family="{MONO}" fill="{c["accent"]}">{esc(name)}{fork_mark}</text>'
        )
        inner.append(
            f'  <text x="772" y="{y}" text-anchor="end" font-size="13" '
            f'font-family="{MONO}" fill="{c["muted"]}">&#9733; {stars}</text>'
        )
        if desc:
            inner.append(
                f'  <text x="28" y="{y + 20}" font-size="12" fill="{c["text"]}">{esc(desc)}</text>'
            )
        if lang:
            dot = LANG_COLORS.get(lang, c["muted"])
            inner.append(
                f'  <circle cx="30" cy="{y + 34}" r="4" fill="{dot}"/>'
                f'<text x="42" y="{y + 38}" font-size="12" fill="{c["muted"]}">{esc(lang)}</text>'
            )
        y += 60

    return svg_doc(theme, y + 14, "\n".join(inner))


# ---------------------------------------------------------------------------
# Clock (commit-hour histogram)
# ---------------------------------------------------------------------------
def commit_hour(iso):
    iso = iso.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(iso)
    except ValueError:
        return None
    return dt.astimezone(CST).hour


def commit_hours(repos):
    if not isinstance(repos, list):
        return [0] * 24
    counts = [0] * 24
    since = (datetime.now(timezone.utc) - timedelta(days=90)).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    for repo in repos[:10]:
        owner = repo.get("owner", {}).get("login", USERNAME)
        name = repo.get("name")
        if not name:
            continue
        try:
            commits = gh(
                f"/repos/{owner}/{name}/commits?author={USERNAME}"
                f"&since={since}&per_page=100"
            )
        except Exception:
            continue
        if not isinstance(commits, list):
            continue
        for cm in commits:
            iso = (cm.get("commit") or {}).get("author", {}).get("date")
            if not iso:
                continue
            h = commit_hour(iso)
            if h is not None:
                counts[h] += 1
    return counts


def build_clock(theme, counts):
    c = THEMES[theme]
    inner = [section_title(theme, 38, "When I Code  ·  24h Asia/Shanghai")]

    if max(counts, default=0) == 0:
        inner.append(
            f'  <text x="400" y="120" text-anchor="middle" font-size="15" '
            f'fill="{c["muted"]}">No commits in the last 90 days.</text>'
        )
        return svg_doc(theme, 158, "\n".join(inner))

    x0, baseline, maxh = 40, 196, 126
    step = (WIDTH - 2 * x0) / 24
    barw = step - 6
    maxc = max(counts)
    peak = counts.index(maxc)

    for i, n in enumerate(counts):
        if not n:
            continue
        x = x0 + i * step
        h = (n / maxc) * maxh
        if h < 3:
            h = 3
        fill = c["accent"] if i == peak else c["accent_soft"]
        inner.append(
            f'  <rect x="{x:.1f}" y="{baseline - h:.1f}" width="{barw:.1f}" '
            f'height="{h:.1f}" rx="3" fill="{fill}"/>'
        )
    for i in (0, 6, 12, 18):
        x = x0 + i * step
        inner.append(
            f'  <text x="{x:.1f}" y="{baseline + 18}" font-size="10" '
            f'text-anchor="middle" fill="{c["muted"]}">{i}</text>'
        )
    inner.append(
        f'  <text x="40" y="{baseline + 36}" font-size="12" fill="{c["muted"]}">'
        f'Most active: {peak}:00 – {peak + 1}:00</text>'
    )
    return svg_doc(theme, 254, "\n".join(inner))


# ---------------------------------------------------------------------------
# Stats (stars / forks / followers / following + top languages)
# ---------------------------------------------------------------------------
def build_stats(theme, user, repos):
    c = THEMES[theme]
    if not isinstance(repos, list):
        repos = []
    total_stars = sum(r.get("stargazers_count", 0) for r in repos)
    total_forks = sum(r.get("forks_count", 0) for r in repos)
    followers = user.get("followers", 0)
    following = user.get("following", 0)

    metrics = [
        (str(total_stars), "Stars"),
        (str(total_forks), "Forks"),
        (str(followers), "Followers"),
        (str(following), "Following"),
    ]
    inner = [section_title(theme, 38, "GitHub Stats")]
    step = (WIDTH - 56) / 4
    for i, (value, label) in enumerate(metrics):
        x = 28 + step * (i + 0.5)
        inner.append(
            f'  <text x="{x:.1f}" y="80" text-anchor="middle" font-size="28" '
            f'font-weight="700" font-family="{MONO}" fill="{c["accent"]}">{esc(value)}</text>'
        )
        inner.append(
            f'  <text x="{x:.1f}" y="106" text-anchor="middle" font-size="13" '
            f'fill="{c["muted"]}">{esc(label)}</text>'
        )

    # Most-used languages (exclude forks, count by repo)
    lang_counts = {}
    for r in repos:
        if r.get("fork"):
            continue
        lang = r.get("language")
        if lang:
            lang_counts[lang] = lang_counts.get(lang, 0) + 1
    top = sorted(lang_counts.items(), key=lambda kv: kv[1], reverse=True)[:4]

    if top:
        total = sum(n for _, n in top)
        inner.append(
            f'  <text x="28" y="124" font-size="12" fill="{c["muted"]}">Most used languages</text>'
        )
        x, by, bw, bh = 28, 132, WIDTH - 56, 12
        for lang, n in top:
            w = bw * n / total
            color = LANG_COLORS.get(lang, c["muted"])
            inner.append(
                f'  <rect x="{x:.1f}" y="{by}" width="{w:.1f}" height="{bh}" fill="{color}"/>'
            )
            x += w
        for i, (lang, n) in enumerate(top):
            color = LANG_COLORS.get(lang, c["muted"])
            pct = round(n * 100 / total)
            label = lang if len(lang) <= 14 else lang[:13] + "…"
            lx = 28 + step * i
            inner.append(
                f'  <circle cx="{lx + 4}" cy="160" r="4" fill="{color}"/>'
                f'<text x="{lx + 16}" y="164" font-size="12" fill="{c["text"]}">'
                f'{esc(label)} {pct}%</text>'
            )
        height = 196
    else:
        height = 134

    return svg_doc(theme, height, "\n".join(inner))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def write(name, svg, theme):
    suffix = "-dark" if theme == "dark" else ""
    path = os.path.join("assets", f"{name}{suffix}.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"wrote {path}")


def main():
    os.makedirs("assets", exist_ok=True)
    user = gh(f"/users/{USERNAME}")
    events = gh(f"/users/{USERNAME}/events/public?per_page=100")
    repos = gh(f"/users/{USERNAME}/repos?per_page=100&sort=pushed")
    counts = commit_hours(repos)

    for theme in ("light", "dark"):
        write("banner", build_banner(theme), theme)
        write("typing", build_typing(theme), theme)
        write("journey", build_journey(theme, user, events), theme)
        write("projects", build_projects(theme, repos), theme)
        write("clock", build_clock(theme, counts), theme)
        write("stats", build_stats(theme, user, repos), theme)
    print("done")


if __name__ == "__main__":
    main()
