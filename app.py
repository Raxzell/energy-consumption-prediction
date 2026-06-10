import streamlit as st
import pandas as pd
import requests
import joblib
from datetime import datetime

# 1. Konfigurasi Halaman
st.set_page_config(page_title="Prediksi Energi Smart Home", layout="centered")

st.title("⚡ Prediksi Energi Rumah Tangga")
st.markdown("Aplikasi untuk memprediksi estimasi penggunaan energi peralatan rumah (Wh) berdasarkan kondisi saat ini.")
st.divider()

# 2. Load Model (sekali saja, pakai cache)
@st.cache_resource
def load_models():
    lr  = joblib.load("lr_pipeline.pkl")
    rf  = joblib.load("rf_pipeline.pkl")
    xgb = joblib.load("xgb_pipeline.pkl")
    return lr, rf, xgb

try:
    pipeline_lr, pipeline_rf, pipeline_xgb = load_models()
    model_loaded = True
except Exception as e:
    st.error(f"❌ Gagal memuat model: {e}\nPastikan file .pkl sudah ada di folder yang sama.")
    model_loaded = False

# 3. Nilai default median dari dataset (untuk sensor internal yang tidak diinput user)
MEDIAN_DEFAULTS = {
    'T1':         21.60,
    'RH_1':       39.66,
    'RH_2':       40.50,
    'T3':         22.10,
    'RH_3':       38.53,
    'T4':         20.67,
    'RH_4':       38.40,
    'T5':         19.39,
    'RH_5':       49.09,
    'T6':          7.30,
    'RH_6':       55.29,
    'T7':         20.03,
    'RH_7':       34.86,
    'T8':         22.10,
    'RH_8':       42.38,
    'T9':         19.39,
    'RH_9':       40.90,
}

# Urutan fitur harus SAMA dengan saat training
FEATURE_ORDER = [
    'lights', 'T1', 'RH_1', 'T2', 'RH_2', 'T3', 'RH_3',
    'T4', 'RH_4', 'T5', 'RH_5', 'T6', 'RH_6', 'T7', 'RH_7',
    'T8', 'RH_8', 'T9', 'RH_9',
    'T_out', 'Press_mm_hg', 'RH_out', 'Windspeed', 'Visibility', 'Tdewpoint'
]

# 4. Inisialisasi State Awal
if 'temp' not in st.session_state:
    st.session_state.update({
        'temp': 6.9, 'humidity': 83.7, 'pressure': 756.1,
        'wind': 3.7, 'visibility': 40.0, 'dewpoint': 3.4
    })

# --- DATABASE KOTA ---
DAFTAR_KOTA = {
    "Jakarta":          (-6.1818, 106.8223),
    "Surabaya":         (-7.2504, 112.7688),
    "Semarang":         (-6.9667, 110.4167),
    "Surakarta (Solo)": (-7.5561, 110.8317),
    "Yogyakarta":       (-7.7956, 110.3695),
    "Bandung":          (-6.9175, 107.6191),
    "Medan":            ( 3.5952,  98.6722),
    "Makassar":         (-5.1477, 119.4327),
    "Denpasar":         (-8.6705, 115.2126),
}

# 5. Input Waktu
st.subheader("Waktu & Tanggal")
col1, col2 = st.columns(2)
with col1:
    input_tanggal = st.date_input("Tanggal", datetime.today())
with col2:
    input_waktu = st.time_input("Jam", datetime.now().time())

# 6. Input Utama
st.subheader("Kondisi Ruangan")
suhu_ruang_utama = st.slider("Suhu Ruang Utama / T2 (°C)", min_value=15.0, max_value=35.0, value=20.0, step=0.5)
watt_lampu = st.number_input("Total Energi Lampu Menyala (Wh)", min_value=0, max_value=200, value=0, step=10)

# --- FUNGSI TARIK API CUACA ---
def fetch_weather_api(lat, lon):
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&current=temperature_2m,relative_humidity_2m,surface_pressure,"
        f"wind_speed_10m,visibility,dew_point_2m"
    )
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()['current']
            st.session_state['temp']       = float(data['temperature_2m'])
            st.session_state['humidity']   = float(data['relative_humidity_2m'])
            st.session_state['pressure']   = float(data['surface_pressure'] * 0.750062)
            st.session_state['wind']       = float(data['wind_speed_10m'] / 3.6)
            st.session_state['visibility'] = float(data['visibility'] / 1000)
            st.session_state['dewpoint']   = float(data['dew_point_2m'])
            return True
    except Exception:
        pass
    return False

# 7. Input Cuaca
with st.expander("Kondisi Cuaca Luar", expanded=True):
    st.caption("Pilih lokasi untuk menarik data cuaca secara otomatis, atau edit angkanya secara manual.")

    kota_pilihan = st.selectbox("Pilih Lokasi:", list(DAFTAR_KOTA.keys()))

    if st.button(f"🔄 Tarik Data Cuaca ({kota_pilihan})"):
        lat_terpilih, lon_terpilih = DAFTAR_KOTA[kota_pilihan]
        sukses = fetch_weather_api(lat_terpilih, lon_terpilih)
        if sukses:
            st.success(f"Berhasil menarik data cuaca realtime untuk {kota_pilihan}!")
        else:
            st.error("Gagal menarik data API, silakan isi manual.")

    col_cuaca1, col_cuaca2 = st.columns(2)
    with col_cuaca1:
        suhu_luar      = st.number_input("Suhu Luar / T_out (°C)",        key="temp")
        kelembapan_luar = st.number_input("Kelembapan Luar / RH_out (%)", key="humidity")
        tekanan_udara  = st.number_input("Tekanan Udara / Press (mmHg)",  key="pressure")
    with col_cuaca2:
        kecepatan_angin = st.number_input("Kecepatan Angin (m/s)",        key="wind")
        visibilitas    = st.number_input("Visibilitas (km)",               key="visibility")
        titik_embun    = st.number_input("Titik Embun / Tdewpoint (°C)",  key="dewpoint")

st.divider()

# 8. Tombol Prediksi
if st.button("⚡ Hitung Prediksi Energi", use_container_width=True):
    if not model_loaded:
        st.error("Model belum berhasil dimuat. Jalankan ulang modeling.ipynb terlebih dahulu.")
    else:
        # Bangun DataFrame dengan semua 25 fitur sesuai urutan training
        row = {**MEDIAN_DEFAULTS}   # mulai dari nilai median default
        row['lights']      = float(watt_lampu)
        row['T2']          = float(suhu_ruang_utama)
        row['T_out']       = float(suhu_luar)
        row['Press_mm_hg'] = float(tekanan_udara)
        row['RH_out']      = float(kelembapan_luar)
        row['Windspeed']   = float(kecepatan_angin)
        row['Visibility']  = float(visibilitas)
        row['Tdewpoint']   = float(titik_embun)

        # Pastikan urutan kolom sama persis dengan saat training
        data_input = pd.DataFrame([row])[FEATURE_ORDER]

        # Prediksi dari 3 model
        hasil_lr  = pipeline_lr.predict(data_input)[0]
        hasil_rf  = pipeline_rf.predict(data_input)[0]
        hasil_xgb = pipeline_xgb.predict(data_input)[0]

        # Tampilkan hasil
        st.success("✅ Prediksi Berhasil!")
        st.markdown("### Perbandingan Hasil Prediksi Model:")

        col_res1, col_res2, col_res3 = st.columns(3)
        with col_res1:
            st.metric(label="Linear Regression", value=f"{hasil_lr:.1f} Wh")
        with col_res2:
            st.metric(label="Random Forest",     value=f"{hasil_rf:.1f} Wh")
        with col_res3:
            st.metric(label="XGBoost",           value=f"{hasil_xgb:.1f} Wh")

        st.caption(
            "ℹ️ Sensor internal (T1, T3–T9, RH_1–RH_9) menggunakan nilai median dataset "
            "karena tidak diinput secara langsung."
        )
