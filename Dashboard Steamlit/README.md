# Dashboard Curah Hujan & Luas Panen Padi — Jawa Barat 2025

Dashboard Streamlit multi-halaman (Kelompok 1 · Big Data) untuk menganalisis hubungan
curah hujan dan luas panen padi di 27 kabupaten/kota Jawa Barat tahun 2025.

## Menjalankan

```bash
pip install -r requirements.txt
streamlit run app.py
```

Buka `http://localhost:8501`.

## Halaman
- **Ringkasan** — KPI + sparkline, scatter korelasi hujan↔panen (Pearson r), rekomendasi jadwal tanam.
- **Curah Hujan** — bar intensitas bulanan, tren + zona intensitas, variabel iklim (suhu/kelembapan/sinar).
- **Luas Panen** — ranking distrik, kontribusi top-8 (donut), heatmap distrik × bulan.
- **Distrik** — telaah satu distrik: panen vs hujan ternormalisasi (0–1), panen bulanan.
- **Data** — tabel kesesuaian per bulan, peringkat distrik, unduhan CSV.

Pilih **Distrik** di sidebar (berlaku lintas halaman).

## Data
- Curah hujan harian 2025 (Excel, BMKG) & luas panen bulanan (CSV, BPS) diambil dari GitHub
  saat dijalankan, lalu diagregasi/klasifikasi seperti di notebook `Kelompok1_BigData_UAS`.
- Bila offline / sumber tak terjangkau, app otomatis memakai data tertanam (`fallback.py`)
  — badge sidebar menunjukkan status **🟢 online** / **🟡 offline**.
- Klasifikasi kesesuaian padi: `<50` Sangat Kritis · `50–100` Kurang · `100–200` Optimal · `>200` Berlebih (mm/bulan).

## Struktur
```
app.py            entry point (st.navigation + sidebar)
data.py           loader + agregasi + fallback (DashboardData)
fallback.py       konstanta data offline
charts.py         builder figure Plotly + statistik
ui.py             CSS, kartu KPI, header, rekomendasi
pages_app/        ringkasan · curah_hujan · luas_panen · distrik · data_page
.streamlit/config.toml   tema gelap
```
