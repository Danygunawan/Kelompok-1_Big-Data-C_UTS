"""Builder figure Plotly (tema gelap) + helper statistik."""
from __future__ import annotations

import numpy as np
import plotly.graph_objects as go

from data import minmax
from ui import COLORS

ACCENT, SKY, AMBER, RED, VIOLET = (
    COLORS["accent"], COLORS["sky"], COLORS["amber"], COLORS["red"], COLORS["violet"])

DONUT_COLORS = ["#10b981", "#0ea5e9", "#6366f1", "#f59e0b", "#ef4444",
                "#14b8a6", "#8b5cf6", "#ec4899", "#475569"]


# --------------------------------------------------------------------------- #
# Helper
# --------------------------------------------------------------------------- #
def _rgba(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def pearson(a, b) -> float:
    a, b = np.asarray(a, float), np.asarray(b, float)
    if a.std() == 0 or b.std() == 0:
        return 0.0
    return float(np.corrcoef(a, b)[0, 1])


def ols_line(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    m, c = np.polyfit(x, y, 1)
    xs = np.array([x.min(), x.max()])
    return xs, m * xs + c


def _base(fig: go.Figure, height: int = 320, legend: bool = False,
          title: str = "") -> go.Figure:
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=COLORS["text2"], size=11),
        margin=dict(l=10, r=10, t=46 if title else 16, b=10),
        height=height, showlegend=legend,
        hoverlabel=dict(bgcolor=COLORS["card"], bordercolor="rgba(255,255,255,0.12)",
                        font=dict(color=COLORS["text"], family="Inter")),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0,
                    font=dict(color=COLORS["text2"], size=11)),
        title=dict(text=title, font=dict(color=COLORS["text"], size=14),
                   x=0.0, xanchor="left", y=0.97),
    )
    fig.update_xaxes(gridcolor=COLORS["grid"], zeroline=False, linecolor=COLORS["grid"])
    fig.update_yaxes(gridcolor=COLORS["grid"], zeroline=False, linecolor=COLORS["grid"])
    return fig


# --------------------------------------------------------------------------- #
# Sparkline (untuk kartu KPI)
# --------------------------------------------------------------------------- #
def sparkline(series, color: str) -> go.Figure:
    y = list(series)
    fig = go.Figure(go.Scatter(
        y=y, mode="lines", line=dict(color=color, width=2, shape="spline"),
        fill="tozeroy", fillcolor=_rgba(color, 0.18), hoverinfo="skip"))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      margin=dict(l=0, r=0, t=0, b=0), height=46, showlegend=False)
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return fig


# --------------------------------------------------------------------------- #
# Curah hujan
# --------------------------------------------------------------------------- #
def fig_rain_bar(data, height: int = 320) -> go.Figure:
    rr = data.rainfall_monthly
    colors = [SKY if v >= 400 else ACCENT for v in rr["rr"]]
    fig = go.Figure(go.Bar(
        x=rr["bulan"], y=rr["rr"], marker_color=colors, marker_line_width=0,
        hovertemplate="%{x}: %{y:.1f} mm<extra></extra>"))
    fig.update_layout(barcornerradius=6)
    _base(fig, height)
    fig.update_yaxes(title_text="mm")
    return fig


def fig_rain_trend(data, height: int = 320) -> go.Figure:
    rr = data.rainfall_monthly
    fig = go.Figure(go.Scatter(
        x=rr["bulan"], y=rr["rr"], mode="lines+markers",
        line=dict(color=ACCENT, width=2, shape="spline"),
        fill="tozeroy", fillcolor=_rgba(ACCENT, 0.12),
        marker=dict(size=7, color=ACCENT),
        hovertemplate="%{x}: %{y:.1f} mm<extra></extra>"))
    bands = [(0, 100, RED), (100, 200, AMBER), (200, 300, "#eab308"), (300, 600, ACCENT)]
    for lo, hi, col in bands:
        fig.add_hrect(y0=lo, y1=hi, fillcolor=_rgba(col, 0.06), line_width=0, layer="below")
    _base(fig, height)
    fig.update_yaxes(title_text="mm")
    return fig


_CLIM_META = {
    "tavg": ("Suhu Rata-rata (°C)", AMBER, "°C"),
    "rh":   ("Kelembapan (%)", SKY, "%"),
    "ss":   ("Lama Penyinaran (jam)", VIOLET, " jam"),
}


def fig_climate_line(data, metric: str, height: int = 320) -> go.Figure:
    label, color, unit = _CLIM_META[metric]
    clm = data.climate_monthly
    fig = go.Figure(go.Scatter(
        x=clm["bulan"], y=clm[metric], mode="lines+markers", name=label,
        line=dict(color=color, width=2, shape="spline"),
        fill="tozeroy", fillcolor=_rgba(color, 0.13),
        marker=dict(size=7, color=color),
        hovertemplate="%{x}: %{y:.2f}" + unit + "<extra></extra>"))
    _base(fig, height, title=label)
    return fig


# --------------------------------------------------------------------------- #
# Luas panen
# --------------------------------------------------------------------------- #
def fig_district_rank(data, height: int = 560) -> go.Figure:
    da = data.district_annual
    names, vals = da.index.tolist(), da.values.tolist()
    colors = [ACCENT if i < 3 else _rgba(ACCENT, 0.45) for i in range(len(names))]
    fig = go.Figure(go.Bar(
        y=names[::-1], x=vals[::-1], orientation="h",
        marker_color=colors[::-1], marker_line_width=0,
        hovertemplate="%{y}: %{x:,.0f} ha<extra></extra>"))
    fig.update_layout(barcornerradius=4)
    _base(fig, height)
    fig.update_xaxes(title_text="ha")
    fig.update_yaxes(tickfont=dict(size=10))
    return fig


def fig_donut(data, topn: int = 8, height: int = 420) -> go.Figure:
    da = data.district_annual
    top = da.iloc[:topn]
    others = float(da.iloc[topn:].sum())
    labels = top.index.tolist() + ["Lainnya"]
    values = top.values.tolist() + [others]
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.62, sort=False,
        marker=dict(colors=DONUT_COLORS, line=dict(color=COLORS["card"], width=2)),
        textinfo="none",
        hovertemplate="%{label}: %{value:,.0f} ha (%{percent})<extra></extra>"))
    _base(fig, height, legend=True)
    fig.update_layout(legend=dict(orientation="v", yanchor="middle", y=0.5,
                                  xanchor="left", x=1.0, font=dict(size=11)))
    return fig


def fig_heatmap(data, height: int = 640) -> go.Figure:
    order = data.district_annual.index.tolist()
    mat = data.harvest_by_district[order].T  # baris=distrik, kolom=bulan
    norm = np.vstack([minmax(mat.loc[d].values) for d in order])
    fig = go.Figure(go.Heatmap(
        z=norm, x=data.months, y=order, colorscale="RdYlGn", zmin=0, zmax=1,
        customdata=mat.values,
        hovertemplate="%{y} · %{x}<br>%{customdata:,.0f} ha (norm %{z:.2f})<extra></extra>",
        colorbar=dict(title="norm", thickness=12, len=0.8)))
    _base(fig, height)
    fig.update_yaxes(autorange="reversed", tickfont=dict(size=9))
    return fig


# --------------------------------------------------------------------------- #
# Distrik
# --------------------------------------------------------------------------- #
def fig_dual_normalized(data, district: str, height: int = 360):
    months = data.months
    harv = data.harvest_by_district[district].values
    rain = data.rainfall_monthly["rr"].values
    nh, nr = minmax(harv), minmax(rain)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=months, y=nh, mode="lines+markers", name=f"Luas Panen — {district}",
        line=dict(color=ACCENT, width=2, shape="spline"),
        fill="tozeroy", fillcolor=_rgba(ACCENT, 0.10), marker=dict(size=6, color=ACCENT),
        customdata=harv, hovertemplate="Panen: %{y:.2f} (%{customdata:,.1f} ha)<extra></extra>"))
    fig.add_trace(go.Scatter(
        x=months, y=nr, mode="lines+markers", name="Curah Hujan",
        line=dict(color=SKY, width=2, dash="dash", shape="spline"), marker=dict(size=5, color=SKY),
        customdata=rain, hovertemplate="Hujan: %{y:.2f} (%{customdata:,.1f} mm)<extra></extra>"))
    _base(fig, height, legend=True)
    fig.update_yaxes(title_text="skala 0–1", range=[-0.02, 1.05])
    return fig, pearson(nh, nr)


def fig_district_monthly(data, district: str, height: int = 300) -> go.Figure:
    vals = data.harvest_by_district[district]
    fig = go.Figure(go.Bar(
        x=data.months, y=vals.values, marker_color=ACCENT, marker_line_width=0,
        hovertemplate="%{x}: %{y:,.1f} ha<extra></extra>"))
    fig.update_layout(barcornerradius=6)
    _base(fig, height)
    fig.update_yaxes(title_text="ha")
    return fig


# --------------------------------------------------------------------------- #
# Korelasi hujan vs panen (provinsi)
# --------------------------------------------------------------------------- #
def fig_scatter_rain_harvest(data, height: int = 380):
    x = data.rainfall_monthly["rr"].values
    y = data.province_total.values
    months = data.months
    r = pearson(x, y)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x, y=y, mode="markers+text", text=months, textposition="top center",
        textfont=dict(size=9, color=COLORS["muted"]),
        marker=dict(size=12, color=ACCENT, line=dict(color="#0f1117", width=1)),
        hovertemplate="%{text}<br>Hujan %{x:.0f} mm<br>Panen %{y:,.0f} ha<extra></extra>",
        name="Bulan"))
    xs, ys = ols_line(x, y)
    fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", name="Tren (OLS)",
                             line=dict(color=SKY, width=2, dash="dash")))
    _base(fig, height, legend=True, title=f"Curah Hujan vs Luas Panen Provinsi · r = {r:.2f}")
    fig.update_xaxes(title_text="Curah hujan (mm)")
    fig.update_yaxes(title_text="Luas panen provinsi (ha)")
    return fig, r
