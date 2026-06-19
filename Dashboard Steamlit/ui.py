"""Komponen UI & tema (CSS injeksi, kartu KPI, header seksi, kartu rekomendasi)."""
from __future__ import annotations

import pandas as pd
import streamlit as st

# Palet warna (sinkron dengan dashboard.html)
COLORS = {
    "bg": "#0f1117", "card": "#1a1d27", "border": "rgba(255,255,255,0.07)",
    "accent": "#10b981", "sky": "#0ea5e9", "amber": "#f59e0b", "red": "#ef4444",
    "violet": "#8b5cf6", "indigo": "#6366f1",
    "text": "#f1f5f9", "text2": "#94a3b8", "muted": "#64748b",
    "grid": "rgba(255,255,255,0.06)",
}

# Kelas kesesuaian -> (nama css pill, warna, ikon, saran)
KELAS_INFO = {
    "Optimal":       ("optimal", COLORS["accent"], "✅", "Ideal untuk tanam padi — kebutuhan air tercukupi."),
    "Berlebih":      ("berlebih", COLORS["sky"], "🌊", "Curah hujan tinggi — waspada genangan, pastikan drainase baik."),
    "Kurang":        ("kurang", COLORS["amber"], "⚠️", "Air kurang — perlu irigasi tambahan sebelum tanam."),
    "Sangat Kritis": ("kritis", COLORS["red"], "🔥", "Sangat kering — tunda tanam / andalkan irigasi penuh."),
}


def fmt(n: float, d: int = 0) -> str:
    return f"{n:,.{d}f}"


def fmt_k(n: float) -> str:
    return f"{n / 1000:,.1f}k" if n >= 1000 else f"{n:,.0f}"


def inject_css() -> None:
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], .stApp, button, input, select, textarea {
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
}
.stApp { background: #0f1117; }
.block-container { padding-top: 2.2rem; padding-bottom: 3rem; max-width: 1320px; }

/* ---- Sidebar ---- */
section[data-testid="stSidebar"] { background: #141722; border-right: 1px solid rgba(255,255,255,0.06); }
.brand { display:flex; align-items:center; gap:10px; padding: 4px 0 2px; }
.brand .logo { font-size: 26px; }
.brand .name {
  font-size: 18px; font-weight: 800; letter-spacing:-0.02em; line-height:1.1;
  background: linear-gradient(90deg,#10b981,#0ea5e9);
  -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
}
.brand-sub { color:#64748b; font-size:11px; margin: 2px 0 6px; }
.src-badge { display:inline-flex; align-items:center; gap:6px; font-size:11px; font-weight:600;
  padding:4px 10px; border-radius:999px; border:1px solid var(--bd); }
.src-online  { color:#10b981; background:rgba(16,185,129,0.12); --bd:rgba(16,185,129,0.35); }
.src-offline { color:#f59e0b; background:rgba(245,158,11,0.12); --bd:rgba(245,158,11,0.35); }
.side-foot { color:#64748b; font-size:11px; margin-top:8px; line-height:1.5; }

/* ---- Section header ---- */
.sec { margin: 6px 0 14px; }
.sec-title { font-size: 22px; font-weight: 800; letter-spacing:-0.02em; color:#f1f5f9; }
.sec-sub { color:#94a3b8; font-size: 13px; margin-top: 3px; max-width: 760px; }

/* ---- KPI card ---- */
.kpi {
  background:#1a1d27; border:1px solid rgba(255,255,255,0.07); border-left:3px solid #475569;
  border-radius:12px; padding:16px 18px; transition:all .2s ease; height:100%;
}
.kpi:hover { transform: translateY(-2px); border-color: rgba(16,185,129,0.25); }
.kpi.up   { border-left-color:#10b981; }
.kpi.info { border-left-color:#0ea5e9; }
.kpi.warn { border-left-color:#f59e0b; }
.kpi.neutral { border-left-color:#475569; }
.kpi-top { display:flex; align-items:center; gap:7px; }
.kpi-icon { font-size:15px; }
.kpi-label { color:#94a3b8; font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:.04em; }
.kpi-value { font-size:26px; font-weight:800; letter-spacing:-0.02em; margin-top:7px; color:#f1f5f9; line-height:1.1; }
.kpi-unit { font-size:13px; font-weight:600; color:#94a3b8; margin-left:4px; }
.kpi-delta { font-size:12px; font-weight:600; margin-top:6px; }
.kpi-delta.up { color:#10b981; } .kpi-delta.info { color:#0ea5e9; }
.kpi-delta.warn { color:#f59e0b; } .kpi-delta.neutral { color:#94a3b8; }

/* tarik sparkline mendekat ke kartu di atasnya */
.kpi + div [data-testid="stPlotlyChart"] { margin-top:-6px; }

/* ---- Pills ---- */
.pill { padding:3px 10px; border-radius:999px; font-size:11px; font-weight:600; white-space:nowrap; }
.pill.optimal  { background:rgba(16,185,129,0.15); color:#10b981; }
.pill.berlebih { background:rgba(14,165,233,0.15); color:#0ea5e9; }
.pill.kurang   { background:rgba(245,158,11,0.15); color:#f59e0b; }
.pill.kritis   { background:rgba(239,68,68,0.15);  color:#ef4444; }

/* ---- Recommendation cards ---- */
.rec-wrap { display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:12px; }
.rec-card { background:#1a1d27; border:1px solid rgba(255,255,255,0.07); border-radius:12px; padding:14px 16px; }
.rec-head { display:flex; align-items:center; justify-content:space-between; gap:8px; margin-bottom:8px; }
.rec-months { font-weight:700; font-size:14px; color:#f1f5f9; }
.rec-text { color:#94a3b8; font-size:12px; line-height:1.5; }

footer, #MainMenu { visibility:hidden; }
</style>
        """,
        unsafe_allow_html=True,
    )


def section_header(title: str, subtitle: str = "", icon: str = "") -> None:
    sub = f'<div class="sec-sub">{subtitle}</div>' if subtitle else ""
    head = f"{icon} {title}".strip()
    st.markdown(f'<div class="sec"><div class="sec-title">{head}</div>{sub}</div>',
                unsafe_allow_html=True)


def kpi_card(label: str, value: str, unit: str = "", delta: str = "",
             cls: str = "neutral", icon: str = "") -> str:
    """Kembalikan HTML kartu KPI (render dengan st.markdown unsafe_allow_html)."""
    unit_html = f'<span class="kpi-unit">{unit}</span>' if unit else ""
    delta_html = f'<div class="kpi-delta {cls}">{delta}</div>' if delta else ""
    icon_html = f'<span class="kpi-icon">{icon}</span>' if icon else ""
    return (
        f'<div class="kpi {cls}">'
        f'<div class="kpi-top">{icon_html}<span class="kpi-label">{label}</span></div>'
        f'<div class="kpi-value">{value}{unit_html}</div>'
        f'{delta_html}</div>'
    )


def pill_class(kelas: str) -> str:
    return KELAS_INFO.get(kelas, ("optimal",))[0]


def _runs(kesesuaian: pd.DataFrame):
    """Kelompokkan bulan berurutan dengan kelas sama."""
    months = kesesuaian["bulan"].tolist()
    kelas = kesesuaian["kelas"].tolist()
    runs, i = [], 0
    while i < len(months):
        j = i
        while j + 1 < len(months) and kelas[j + 1] == kelas[i]:
            j += 1
        label = months[i] if i == j else f"{months[i]}–{months[j]}"
        runs.append((label, kelas[i]))
        i = j + 1
    return runs


def recommendation_cards(kesesuaian: pd.DataFrame) -> None:
    cards = []
    for label, kelas in _runs(kesesuaian):
        pill, _color, icon, advice = KELAS_INFO.get(
            kelas, ("optimal", COLORS["accent"], "•", ""))
        cards.append(
            f'<div class="rec-card">'
            f'<div class="rec-head"><span class="rec-months">{icon} {label}</span>'
            f'<span class="pill {pill}">{kelas}</span></div>'
            f'<div class="rec-text">{advice}</div></div>'
        )
    st.markdown(f'<div class="rec-wrap">{"".join(cards)}</div>', unsafe_allow_html=True)
