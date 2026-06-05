import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# 1. Konfigurasi Halaman (Desain Minimalis)
st.set_page_config(page_title="Prediksi Energi Smart Home", layout="centered")

st.title("⚡ Prediksi Energi Rumah Tangga")
st.markdown("Aplikasi untuk memprediksi estimasi penggunaan energi peralatan rumah (Wh) berdasarkan kondisi saat ini.")
st.divider()

# 2. Input Waktu
st.subheader("Waktu & Tanggal")
col1, col2 = st.columns(2)
with col1:
    input_tanggal = st.date_input("Tanggal", datetime.today())
with col2:
    input_waktu = st.time_input("Jam", datetime.now().time())

# 3. Input Utama dari User
st.subheader("Kondisi Ruangan")
suhu_ruang_utama = st.slider("Suhu Ruang Utama / T2 (°C)", min_value=15.0, max_value=35.0, value=25.0, step=0.5)
watt_lampu = st.number_input("Total Energi Lampu Menyala (Wh)", min_value=0, max_value=200, value=30, step=10)

# --- FUNGSI TARIK API CUACA ---
def fetch_weather_api():
    # Kordinat Jakarta (Bisa diubah dinamis ntar sama temen lu)
    lat, lon = -6.1818, 106.8223 
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,surface_pressure,wind_speed_10m,visibility,dew_point_2m"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()['current']
            # Konversi satuan menyesuaikan dataset energydata_complete
            st.session_state['temp'] = float(data['temperature_2m'])
            st.session_state['humidity'] = float(data['relative_humidity_2m'])
            st.session_state['pressure'] = float(data['surface_pressure'] * 0.750062) # hPa ke mmHg
            st.session_state['wind'] = float(data['wind_speed_10m'] / 3.6) # km/h ke m/s
            st.session_state['visibility'] = float(data['visibility'] / 1000) # meter ke km
            st.session_state['dewpoint'] = float(data['dew_point_2m'])
            return True
    except Exception as e:
        return False
    return False

# Inisialisasi default value awal (biar form gak error sebelum diload)
if 'temp' not in st.session_state:
    st.session_state.update({
        'temp': 28.0, 'humidity': 75.0, 'pressure': 733.0,
        'wind': 5.0, 'visibility': 40.0, 'dewpoint': 5.0
    })
# ------------------------------

# 4. Input Tambahan (Bisa ditarik API & Diedit Manual)
with st.expander("Kondisi Cuaca Luar", expanded=True):
    st.caption("Data cuaca bisa ditarik otomatis sesuai lokasi, atau diisi/edit secara manual.")
    
    if st.button("🔄 Tarik Data Cuaca Saat Ini (Jakarta)"):
        sukses = fetch_weather_api()
        if sukses:
            st.success("Berhasil menarik data cuaca realtime!")
        else:
            st.error("Gagal menarik data API, silakan isi manual.")
            
    col_cuaca1, col_cuaca2 = st.columns(2)
    # Value ngambil dari session_state, tapi tetap bisa ditimpa manual sama user
    with col_cuaca1:
        suhu_luar = st.number_input("Suhu Luar / T_out (°C)", value=st.session_state['temp'])
        kelembapan_luar = st.number_input("Kelembapan Luar / RH_out (%)", value=st.session_state['humidity'])
        tekanan_udara = st.number_input("Tekanan Udara / Press (mmHg)", value=st.session_state['pressure'])
    with col_cuaca2:
        kecepatan_angin = st.number_input("Kecepatan Angin (m/s)", value=st.session_state['wind'])
        visibilitas = st.number_input("Visibilitas (km)", value=st.session_state['visibility'])
        titik_embun = st.number_input("Titik Embun / Tdewpoint (°C)", value=st.session_state['dewpoint'])

st.divider()

# 5. Tombol Eksekusi dan Output (TIDAK BERUBAH)
if st.button("Hitung Prediksi Energi", use_container_width=True):
    
    # --- BAGIAN UNTUK TEMAN BACKEND-MU ---
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
    
    hasil_lr = 120.5 
    hasil_svr = 118.2
    hasil_rf = 125.0
    # --- AKHIR BAGIAN BACKEND ---

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
