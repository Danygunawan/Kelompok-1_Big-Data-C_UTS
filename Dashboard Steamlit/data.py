"""
Lapisan data dashboard.

`load_data()` mencoba mengambil data mentah dari GitHub (Excel hujan harian +
CSV luas panen), lalu mereproduksi agregasi/klasifikasi/normalisasi seperti di
notebook. Jika gagal (mis. tanpa internet), otomatis jatuh ke data offline yang
sudah tervalidasi di `fallback.py`. Hasilnya selalu berbentuk `DashboardData`
yang sama, sehingga semua halaman aman dipakai apa pun sumbernya.
"""
from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO

import numpy as np
import pandas as pd
import streamlit as st

import fallback as fb

# Sumber data mentah (sama seperti notebook)
URL_HUJAN = "https://github.com/Danygunawan/Kelompok-1_Big-Data-C_UTS/raw/refs/heads/main/Data_Curah_Hujan_Jawa_Barat_2025.xlsx"
URL_PANEN = "https://raw.githubusercontent.com/Danygunawan/Kelompok-1_Big-Data-C_UTS/refs/heads/main/Data%20Luas%20Panen%20Padi%20Jawa%20Barat%202025%20CLEANED.csv"

MONTHS = fb.MONTHS
KELAS_ORDER = ["Sangat Kritis", "Kurang", "Optimal", "Berlebih"]

# Nama bulan panjang (CSV) -> indeks bulan 0..11
_LONG_TO_IDX = {
    "januari": 0, "februari": 1, "maret": 2, "april": 3, "mei": 4, "juni": 5,
    "juli": 6, "agustus": 7, "september": 8, "oktober": 9, "november": 10, "desember": 11,
}


# --------------------------------------------------------------------------- #
# Helper
# --------------------------------------------------------------------------- #
def minmax(values) -> np.ndarray:
    """Normalisasi Min-Max ke rentang 0..1 (aman untuk deret datar)."""
    arr = np.asarray(values, dtype=float)
    lo, hi = np.nanmin(arr), np.nanmax(arr)
    rng = (hi - lo) or 1.0
    return (arr - lo) / rng


def classify(ch: float, mn: float = 100, mx: float = 200) -> str:
    """Klasifikasi kesesuaian tanam padi berdasarkan curah hujan bulanan (mm)."""
    if ch < mn * 0.5:
        return "Sangat Kritis"
    if ch < mn:
        return "Kurang"
    if ch <= mx:
        return "Optimal"
    return "Berlebih"


# --------------------------------------------------------------------------- #
# Kontrak data
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class DashboardData:
    months: list                      # 12 nama bulan (pendek)
    rainfall_monthly: pd.DataFrame    # bulan, rr
    climate_monthly: pd.DataFrame     # bulan, tavg, rh, ss
    harvest_by_district: pd.DataFrame # index=bulan (12), kolom=27 distrik (ha)
    province_total: pd.Series         # index=bulan (12), ha
    district_annual: pd.Series        # index=distrik (27), terurut desc, ha
    kesesuaian: pd.DataFrame          # bulan, ch, kelas
    metrics: dict                     # KPI skalar
    source: str                       # "online" | "offline"


# --------------------------------------------------------------------------- #
# Perakitan (dipakai jalur online & offline → struktur identik)
# --------------------------------------------------------------------------- #
def _build_metrics(rr, climate, province_total, district_annual, kesesuaian) -> dict:
    counts = kesesuaian["kelas"].value_counts()
    return {
        "total_rain_mm": float(rr.sum()),
        "avg_monthly_rain": float(rr.mean()),
        "peak_rain_month": str(rr.idxmax()),
        "peak_rain_value": float(rr.max()),
        "low_rain_month": str(rr.idxmin()),
        "low_rain_value": float(rr.min()),
        "province_annual_harvest_ha": float(province_total.sum()),
        "peak_harvest_month": str(province_total.idxmax()),
        "peak_harvest_value": float(province_total.max()),
        "low_harvest_month": str(province_total.idxmin()),
        "low_harvest_value": float(province_total.min()),
        "n_districts": int(district_annual.shape[0]),
        "top_district": str(district_annual.index[0]),
        "top_district_value": float(district_annual.iloc[0]),
        "n_optimal_months": int(counts.get("Optimal", 0)),
        "n_berlebih_months": int(counts.get("Berlebih", 0)),
        "n_kurang_months": int(counts.get("Kurang", 0)),
        "n_kritis_months": int(counts.get("Sangat Kritis", 0)),
        "avg_temp": float(climate["tavg"].mean()),
        "avg_humidity": float(climate["rh"].mean()),
        "avg_sunshine": float(climate["ss"].mean()),
    }


def _assemble(rainfall, climate_dict, by_district, source, threshold) -> DashboardData:
    rr = pd.Series(rainfall, index=MONTHS, name="rr").astype(float)
    climate = pd.DataFrame(
        {"tavg": climate_dict["tavg"], "rh": climate_dict["rh"], "ss": climate_dict["ss"]},
        index=MONTHS,
    ).astype(float)
    harvest = pd.DataFrame(by_district, index=MONTHS).astype(float)

    province_total = harvest.sum(axis=1).rename("province_total")
    district_annual = harvest.sum(axis=0).sort_values(ascending=False).rename("luas_panen")

    mn, mx = threshold["min"], threshold["max"]
    kelas = rr.map(lambda v: classify(v, mn, mx))
    kesesuaian = pd.DataFrame({"bulan": MONTHS, "ch": rr.values, "kelas": kelas.values})

    rainfall_monthly = rr.rename_axis("bulan").reset_index()
    climate_monthly = climate.rename_axis("bulan").reset_index()

    metrics = _build_metrics(rr, climate, province_total, district_annual, kesesuaian)

    return DashboardData(
        months=list(MONTHS),
        rainfall_monthly=rainfall_monthly,
        climate_monthly=climate_monthly,
        harvest_by_district=harvest,
        province_total=province_total,
        district_annual=district_annual,
        kesesuaian=kesesuaian,
        metrics=metrics,
        source=source,
    )


# --------------------------------------------------------------------------- #
# Jalur offline
# --------------------------------------------------------------------------- #
def _build_offline() -> DashboardData:
    return _assemble(
        rainfall=fb.FALLBACK["rainfall"],
        climate_dict=fb.FALLBACK["climate"],
        by_district=fb.FALLBACK["by_district"],
        source="offline",
        threshold=fb.FALLBACK["padi_threshold"],
    )


# --------------------------------------------------------------------------- #
# Jalur online (best-effort; gagal → fallback)
# --------------------------------------------------------------------------- #
def _fetch(url: str, timeout: int = 8) -> bytes:
    import requests  # dependensi streamlit
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    return resp.content


def _load_online() -> DashboardData:
    # --- Curah hujan harian -> agregasi bulanan ---
    rdf = pd.read_excel(BytesIO(_fetch(URL_HUJAN)), engine="openpyxl")
    rdf.columns = [str(c).strip() for c in rdf.columns]
    rdf["TANGGAL"] = pd.to_datetime(rdf["TANGGAL"], dayfirst=True, errors="coerce")
    rdf = rdf.dropna(subset=["TANGGAL"])
    rdf["__m"] = rdf["TANGGAL"].dt.month
    for col in ["RR", "TAVG", "RH_AVG", "SS"]:
        rdf[col] = pd.to_numeric(rdf[col], errors="coerce").replace([8888, 9999], np.nan)

    monthly_rr = rdf.groupby("__m")["RR"].sum().reindex(range(1, 13))
    monthly_clim = rdf.groupby("__m")[["TAVG", "RH_AVG", "SS"]].mean().reindex(range(1, 13))
    if monthly_rr.isna().any() or len(monthly_rr) != 12:
        raise ValueError("Agregasi curah hujan tidak lengkap (12 bulan).")

    rainfall = monthly_rr.round(1).tolist()
    climate_dict = {
        "tavg": monthly_clim["TAVG"].round(1).tolist(),
        "rh": monthly_clim["RH_AVG"].round(1).tolist(),
        "ss": monthly_clim["SS"].round(2).tolist(),
    }

    # --- Luas panen bulanan per distrik ---
    pdf = pd.read_csv(BytesIO(_fetch(URL_PANEN)))
    pdf.columns = [str(c).strip() for c in pdf.columns]
    bulan_col = pdf.columns[0]  # "Bulan Panen"
    pdf[bulan_col] = pdf[bulan_col].astype(str).str.strip()
    pdf["__idx"] = pdf[bulan_col].str.lower().map(_LONG_TO_IDX)
    pdf = pdf.dropna(subset=["__idx"]).sort_values("__idx")
    if len(pdf) != 12:
        raise ValueError("Data luas panen bukan 12 bulan.")

    drop_cols = {bulan_col, "__idx", "Provinsi Jawa Barat"}
    district_cols = [c for c in pdf.columns if c not in drop_cols]
    by_district = {
        c: pd.to_numeric(pdf[c], errors="coerce").fillna(0.0).tolist()
        for c in district_cols
    }
    if not by_district:
        raise ValueError("Kolom distrik tidak ditemukan.")

    return _assemble(rainfall, climate_dict, by_district, "online",
                     fb.FALLBACK["padi_threshold"])


# --------------------------------------------------------------------------- #
# Entry point (cached)
# --------------------------------------------------------------------------- #
@st.cache_data(show_spinner="Memuat & mengolah data…", ttl=3600)
def load_data() -> DashboardData:
    try:
        return _load_online()
    except Exception:
        return _build_offline()
