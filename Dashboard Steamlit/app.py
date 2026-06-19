"""
Dashboard Curah Hujan & Luas Panen Padi — Jawa Barat 2025 (Kelompok 1, Big Data).

Aplikasi Streamlit multi-halaman. Jalankan dari folder ini:
    streamlit run app.py
"""
import streamlit as st

import ui
from data import load_data

st.set_page_config(
    page_title="Curah Hujan & Luas Panen Padi — Jawa Barat 2025",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)
ui.inject_css()

data = load_data()
st.session_state.setdefault("district", data.district_annual.index[0])

# --- Definisi halaman ---
from pages_app import curah_hujan, data_page, distrik, luas_panen, ringkasan  # noqa: E402

nav = st.navigation([
    st.Page(ringkasan.page,   title="Ringkasan",   icon="📊", url_path="ringkasan", default=True),
    st.Page(curah_hujan.page, title="Curah Hujan", icon="🌧️", url_path="curah-hujan"),
    st.Page(luas_panen.page,  title="Luas Panen",  icon="🌾", url_path="luas-panen"),
    st.Page(distrik.page,     title="Distrik",     icon="📍", url_path="distrik"),
    st.Page(data_page.page,   title="Data",        icon="🗂️", url_path="data"),
])

# --- Branding & kontrol sidebar (di bawah menu navigasi) ---
with st.sidebar:
    st.markdown(
        '<div class="brand"><span class="logo">🌾</span>'
        '<span class="name">Jabar Padi 2025</span></div>'
        '<div class="brand-sub">Curah Hujan & Luas Panen Padi</div>',
        unsafe_allow_html=True,
    )
    if data.source == "online":
        st.markdown('<span class="src-badge src-online">🟢 Data online (GitHub)</span>',
                    unsafe_allow_html=True)
    else:
        st.markdown('<span class="src-badge src-offline">🟡 Mode offline (data tertanam)</span>',
                    unsafe_allow_html=True)
    st.divider()
    st.selectbox("Distrik (panen vs hujan)",
                 options=list(data.district_annual.index), key="district")
    st.divider()
    st.markdown('<div class="side-foot">Kelompok 1 · Big Data<br>'
                'BMKG &amp; BPS Jawa Barat 2025</div>', unsafe_allow_html=True)

nav.run()
