import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# 1. Konfigurasi Halaman
st.set_page_config(page_title="Prediksi Energi Smart Home", layout="centered")

st.title("⚡ Prediksi Energi Rumah Tangga")
st.markdown("Aplikasi untuk memprediksi estimasi penggunaan energi peralatan rumah (Wh) berdasarkan kondisi saat ini.")
st.divider()

# 2. Inisialisasi State Awal (DITAMBAH TANGGAL & WAKTU DI SINI)
if 'temp' not in st.session_state:
    st.session_state.update({
        'temp': 28.0, 'humidity': 75.0, 'pressure': 733.0,
        'wind': 5.0, 'visibility': 40.0, 'dewpoint': 5.0,
        # Set default tanggal & jam saat aplikasi pertama kali dibuka
        'tanggal': datetime.today().date(),
        'waktu': datetime.now().time()
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
# ---------------------

# 3. Input Waktu (DIPERBAIKI: PAKE KEY)
st.subheader("Waktu & Tanggal")
col1, col2 = st.columns(2)
with col1:
    input_tanggal = st.date_input("Tanggal", key="tanggal")
with col2:
    input_waktu = st.time_input("Jam", key="waktu")

# 4. Input Utama
st.subheader("Kondisi Ruangan")
suhu_ruang_utama = st.slider("Suhu Ruang Utama / T2 (°C)", min_value=15.0, max_value=35.0, value=25.0, step=0.5)
watt_lampu = st.number_input("Total Energi Lampu Menyala (Wh)", min_value=0, max_value=200, value=30, step=10)

# --- FUNGSI TARIK API CUACA ---
def fetch_weather_api(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,surface_pressure,wind_speed_10m,visibility,dew_point_2m"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()['current']
            st.session_state['temp'] = float(data['temperature_2m'])
            st.session_state['humidity'] = float(data['relative_humidity_2m'])
            st.session_state['pressure'] = float(data['surface_pressure'] * 0.750062) 
            st.session_state['wind'] = float(data['wind_speed_10m'] / 3.6) 
            st.session_state['visibility'] = float(data['visibility'] / 1000) 
            st.session_state['dewpoint'] = float(data['dew_point_2m'])
            return True
    except Exception as e:
        return False
    return False
# -----------------------------------------------------------

# 5. Input Cuaca
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
        suhu_luar = st.number_input("Suhu Luar / T_out (°C)", key="temp")
        kelembapan_luar = st.number_input("Kelembapan Luar / RH_out (%)", key="humidity")
        tekanan_udara = st.number_input("Tekanan Udara / Press (mmHg)", key="pressure")
    with col_cuaca2:
        kecepatan_angin = st.number_input("Kecepatan Angin (m/s)", key="wind")
        visibilitas = st.number_input("Visibilitas (km)", key="visibility")
        titik_embun = st.number_input("Titik Embun / Tdewpoint (°C)", key="dewpoint")

st.divider()

# 6. Tombol Eksekusi
if st.button("Hitung Prediksi Energi", use_container_width=True):
    
    # Nanti temanmu bisa pakai variabel `input_tanggal` dan `input_waktu` ini buat di-extract
    # jadi hari_dalam_seminggu, bulan, atau jam untuk masuk ke model ML.
    
    data_input = pd.DataFrame({
        'T2': [suhu_ruang_utama],
        'lights': [watt_lampu],
        'T_out': [suhu_luar],
        'RH_out': [kelembapan_luar],
        'Press_mm_hg': [tekanan_udara],
        'Windspeed': [kecepatan_angin],
        'Visibility': [visibilitas],
        'Tdewpoint': [titik_embun]
    })
    
    # Simulasi hasil prediksi
    hasil_lr = 120.5 
    hasil_svr = 118.2
    hasil_rf = 125.0

    st.success("Prediksi Berhasil Diproses!")
    st.markdown("### Perbandingan Hasil Prediksi Model:")
    
    col_res1, col_res2, col_res3 = st.columns(3)
    with col_res1:
        st.metric(label="Linear Regression", value=f"{hasil_lr} Wh")
    with col_res2:
        st.metric(label="SVR", value=f"{hasil_svr} Wh")
    with col_res3:
        st.metric(label="Random Forest", value=f"{hasil_rf} Wh")
        
    st.info("Catatan: Nilai di atas masih berupa simulasi dari frontend.")
