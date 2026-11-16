"""Render the stats card and the top-languages card as self-contained SVGs."""
from html import escape

# theme
BG = "#0d0a18"
CARD2 = "#120d22"
BORDER = "#3b2470"
FG = "#f3eeff"
MUTED = "#8d84aa"
ACCENT = "#8b5cf6"
SOFT = "#c4b5fd"
TRACK = "#231a3a"
RING = {"A+": "#34d399", "A": "#34d399", "A-": "#a3e635", "B+": "#fbbf24",
        "B": "#fbbf24", "B-": "#fb923c", "C": "#f87171"}

# a few common GitHub language colors (fallback = accent)
LANG_COLORS = {
    "Python": "#3572A5", "Shell": "#89e051", "Batchfile": "#C1F12E", "HTML": "#e34c26",
    "CSS": "#563d7c", "JavaScript": "#f1e05a", "TypeScript": "#3178c6", "Java": "#b07219",
    "C": "#555555", "C++": "#f34b7d", "C#": "#178600", "Go": "#00ADD8", "Rust": "#dea584",
    "Ruby": "#701516", "PHP": "#4F5D95", "Dockerfile": "#384d54", "PowerShell": "#012456",
    "Jupyter Notebook": "#DA5B0B", "Makefile": "#427819", "Lua": "#000080", "Vue": "#41b883",
}


def _font(size, weight=400, fill=FG):
    return (f'font-family="Segoe UI, Ubuntu, system-ui, sans-serif" '
            f'font-size="{size}" font-weight="{weight}" fill="{fill}"')


def human(n):
    if n >= 1000:
        return f"{n/1000:.1f}".rstrip("0").rstrip(".") + "k"
    return str(n)


def grade(stats):
    """A rough letter grade from overall activity (stars weigh most)."""
    score = (stats["stars"] * 12 + stats["commits"] * 1 + stats["prs"] * 4
             + stats["issues"] * 2 + stats["followers"] * 6 + stats["contributed"] * 3)
    for g, cut in [("A+", 1800), ("A", 900), ("A-", 450), ("B+", 220), ("B", 100), ("B-", 40)]:
        if score >= cut:
            return g, min(1.0, score / 1800)
    return "C", min(1.0, score / 40) * 0.5


# ---- icons (simple inline paths, 20x20 viewport scaled) ----
ICONS = {
    "star": "M10 1.5l2.6 5.3 5.9.9-4.3 4.1 1 5.8L10 15l-5.2 2.6 1-5.8L1.5 7.7l5.9-.9z",
    "commit": "M10 6a4 4 0 1 0 0 8 4 4 0 0 0 0-8zm0-5v3m0 12v3m9-9h-3M4 10H1",
    "pr": "M5 4a2 2 0 1 0 0 4 2 2 0 0 0 0-4zm0 4v8m0 0a2 2 0 1 0 0 0zM15 6a2 2 0 1 0 0-4 2 2 0 0 0 0 4zm0 0v6a3 3 0 0 1-3 3H8",
    "issue": "M10 2a8 8 0 1 0 0 16 8 8 0 0 0 0-16zm0 4v5m0 3h.01",
    "repo": "M4 2h9a2 2 0 0 1 2 2v13l-4-2-4 2V4H4a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h11",
    "follow": "M7 10a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7zm-5 7a5 5 0 0 1 10 0M15 7v6m3-3h-6",
}


def stats_card(stats):
    W, H = 500, 300
    g, pct = grade(stats)
    ring_col = RING.get(g, ACCENT)
    rows = [
        ("star", "Total Stars Earned", human(stats["stars"])),
        ("commit", f"Total Commits ({stats['since']})", human(stats["commits"])),
        ("pr", "Total Pull Requests", human(stats["prs"])),
        ("issue", "Total Issues", human(stats["issues"])),
        ("repo", "Contributed to", human(stats["contributed"])),
        ("follow", "Followers", human(stats["followers"])),
    ]
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img">']
    out.append(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="18" fill="{BG}" stroke="{BORDER}" stroke-width="1.5"/>')
    out.append(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="18" fill="url(#gl)"/>')
    out.append(f'<defs><radialGradient id="gl" cx="18%" cy="8%" r="90%">'
               f'<stop offset="0" stop-color="{ACCENT}" stop-opacity="0.14"/>'
               f'<stop offset="0.6" stop-color="{ACCENT}" stop-opacity="0"/></radialGradient></defs>')
    out.append(f'<text x="32" y="48" {_font(21, 700, SOFT)}>{escape(stats["name"])}’s GitHub Stats</text>')
    out.append(f'<rect x="32" y="62" width="280" height="2" fill="{TRACK}"/>')

    y = 104
    for icon, label, val in rows:
        out.append(f'<g transform="translate(34 {y-14})"><path d="{ICONS[icon]}" fill="none" '
                   f'stroke="{SOFT}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" '
                   f'transform="scale(0.92)"/></g>')
        out.append(f'<text x="64" y="{y}" {_font(15, 400, MUTED)}>{label}:</text>')
        out.append(f'<text x="300" y="{y}" {_font(15, 700, FG)} text-anchor="end">{val}</text>')
        y += 33

    # grade ring
    cx, cy, r = 408, 150, 54
    import math
    circ = 2 * math.pi * r
    dash = circ * pct
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{TRACK}" stroke-width="10"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{ring_col}" stroke-width="10" '
               f'stroke-linecap="round" stroke-dasharray="{dash:.1f} {circ:.1f}" '
               f'transform="rotate(-90 {cx} {cy})"/>')
    out.append(f'<text x="{cx}" y="{cy+9}" {_font(30, 800, FG)} text-anchor="middle">{g}</text>')
    out.append(f'<text x="{cx}" y="{cy+r+30}" {_font(12, 400, MUTED)} text-anchor="middle">activity grade</text>')
    out.append("</svg>")
    return "\n".join(out)


def langs_card(langs):
    """langs: list of (name, bytes) already sorted desc."""
    W = 360
    top = langs[:6]
    total = sum(b for _, b in top) or 1
    rowH = 26
    H = 96 + rowH * len(top)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img">']
    out.append(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="18" fill="{BG}" stroke="{BORDER}" stroke-width="1.5"/>')
    out.append(f'<text x="28" y="44" {_font(20, 700, SOFT)}>Most Used Languages</text>')
    out.append(f'<rect x="28" y="56" width="250" height="2" fill="{TRACK}"/>')

    # stacked bar
    bx, bw, by = 28, W - 56, 76
    x = bx
    out.append(f'<clipPath id="bar"><rect x="{bx}" y="{by}" width="{bw}" height="12" rx="6"/></clipPath>')
    out.append(f'<g clip-path="url(#bar)">')
    for name, b in top:
        seg = bw * b / total
        out.append(f'<rect x="{x:.1f}" y="{by}" width="{seg+0.6:.1f}" height="12" '
                   f'fill="{LANG_COLORS.get(name, ACCENT)}"/>')
        x += seg
    out.append(f'<rect x="{x:.1f}" y="{by}" width="{bx+bw-x+1:.1f}" height="12" fill="{TRACK}"/>')
    out.append("</g>")

    # legend (two columns)
    y = 116
    for i, (name, b) in enumerate(top):
        col = i % 2
        lx = 28 + col * (W // 2 - 10)
        if col == 0 and i:
            y += rowH
        yy = y if col == 0 else y
        pct = b / total * 100
        out.append(f'<circle cx="{lx+6}" cy="{yy-4}" r="6" fill="{LANG_COLORS.get(name, ACCENT)}"/>')
        out.append(f'<text x="{lx+20}" y="{yy}" {_font(13, 400, FG)}>{escape(name)} '
                   f'<tspan fill="{MUTED}">{pct:.1f}%</tspan></text>')
    out.append("</svg>")
    return "\n".join(out)
