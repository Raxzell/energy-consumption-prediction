import streamlit as st
import pandas as pd
import joblib
import requests
import numpy as np

# Load Model
@st.cache_resource
def load_models():
    rf_model = joblib.load("rf_pipeline.pkl")
    xgb_model = joblib.load("xgb_pipeline.pkl")
    return rf_model, xgb_model

rf_model, xgb_model = load_models()

# 1. Konfigurasi Halaman
st.set_page_config(page_title="Prediksi Energi Smart Home", layout="centered")

st.title("Prediksi Energi Rumah Tangga")
st.markdown(
    "Aplikasi untuk memprediksi estimasi penggunaan energi peralatan rumah (Wh) "
    "berdasarkan kondisi saat ini."
)
st.divider()

# 2. Inisialisasi State Awal
if 'temp' not in st.session_state:
    st.session_state.update({
        'temp': 28.0,
        'humidity': 75.0,
        'pressure': 733.0,
        'wind': 5.0,
        'visibility': 40.0,
        'dewpoint': 5.0
    })

# --- DATABASE KOTA ---
DAFTAR_KOTA = {
    "Jakarta": (-6.1818, 106.8223),
    "Surabaya": (-7.2504, 112.7688),
    "Semarang": (-6.9667, 110.4167),
    "Surakarta (Solo)": (-7.5561, 110.8317),
    "Yogyakarta": (-7.7956, 110.3695),
    "Bandung": (-6.9175, 107.6191),
    "Medan": (3.5952, 98.6722),
    "Makassar": (-5.1477, 119.4327),
    "Denpasar": (-8.6705, 115.2126)
}

# 3. Input Utama
st.subheader("Kondisi Ruangan")

suhu_ruang_utama = st.slider(
    "Suhu Ruang Utama / T2 (°C)",
    min_value=15.0,
    max_value=35.0,
    value=25.0,
    step=0.5
)

watt_lampu = st.number_input(
    "Total Energi Lampu Menyala (Wh)",
    min_value=0,
    max_value=200,
    value=30,
    step=10
)

# --- FUNGSI TARIK API CUACA ---
def fetch_weather_api(lat, lon):
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}"
        f"&longitude={lon}"
        "&current=temperature_2m,relative_humidity_2m,"
        "surface_pressure,wind_speed_10m,visibility,dew_point_2m"
    )

    try:
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()['current']

            st.session_state['temp'] = float(data['temperature_2m'])
            st.session_state['humidity'] = float(data['relative_humidity_2m'])

            # hPa ke mmHg
            st.session_state['pressure'] = float(data['surface_pressure'] * 0.750062)

            # km/h ke m/s
            st.session_state['wind'] = float(data['wind_speed_10m'] / 3.6)

            # meter ke km
            st.session_state['visibility'] = float(data['visibility'] / 1000)

            st.session_state['dewpoint'] = float(data['dew_point_2m'])

            return True

    except Exception:
        return False

    return False

# 4. Input Cuaca
with st.expander("Kondisi Cuaca Luar", expanded=True):
    st.caption(
        "Pilih lokasi untuk menarik data cuaca secara otomatis, "
        "atau edit angkanya secara manual."
    )

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
        suhu_luar = st.number_input("Suhu Luar / T_out (°C)", key="temp")
        kelembapan_luar = st.number_input("Kelembapan Luar / RH_out (%)", key="humidity")
        tekanan_udara = st.number_input("Tekanan Udara / Press (mmHg)", key="pressure")

    with col_cuaca2:
        kecepatan_angin = st.number_input("Kecepatan Angin (m/s)", key="wind")
        visibilitas = st.number_input("Visibilitas (km)", key="visibility")
        titik_embun = st.number_input("Titik Embun / Tdewpoint (°C)", key="dewpoint")

st.divider()

# 5. Tombol Eksekusi
if st.button("Hitung Prediksi Energi", use_container_width=True):

    data_input = pd.DataFrame({
        'lights': [watt_lampu],
        'T1': [21.6],
        'RH_1': [39.6],
        'T2': [suhu_ruang_utama],
        'RH_2': [40.5],
        'T3': [22.1],
        'RH_3': [38.5],
        'T4': [20.6],
        'RH_4': [38.4],
        'T5': [19.4],
        'RH_5': [49.0],
        'T6': [7.3],
        'RH_6': [55.2],
        'T7': [20.0],
        'RH_7': [34.8],
        'T8': [22.1],
        'RH_8': [43.7],
        'T9': [19.4],
        'RH_9': [40.9],
        'T_out': [suhu_luar],
        'Press_mm_hg': [tekanan_udara],
        'RH_out': [kelembapan_luar],
        'Windspeed': [kecepatan_angin],
        'Visibility': [visibilitas],
        'Tdewpoint': [titik_embun]
    })

    # Memaksa semua tipe data menjadi float sebelum masuk model
    data_input = data_input.astype(float)

    try:
        # np.ravel memastikan output model dirapikan jadi array 1D
        hasil_xgb = float(np.ravel(xgb_model.predict(data_input))[0])
        hasil_rf = float(np.ravel(rf_model.predict(data_input))[0])

        st.success("Prediksi Berhasil Diproses!")
        st.markdown("### Perbandingan Hasil Prediksi Model:")

        col_res1, col_res2 = st.columns(2)

        with col_res1:
            st.metric(label="XGBoost", value=f"{hasil_xgb:.1f} Wh")

        with col_res2:
            st.metric(label="Random Forest", value=f"{hasil_rf:.1f} Wh")

        st.info("Catatan: Nilai di atas sudah dibulatkan maksimal 1 angka di belakang koma.")

    except Exception as e:
        st.error("🚨 TERJADI ERROR SAAT MODEL MELAKUKAN PREDIKSI!")
        st.code(f"Tipe Error: {type(e).__name__}\nPesan Detail: {str(e)}")
        st.warning(
            "Kalau muncul kotak merah ini, copy-paste isi teks kodenya ke sini "
            "biar langsung dibenerin."
        )
