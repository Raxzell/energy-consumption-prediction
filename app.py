import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Konfigurasi Halaman (Desain Minimalis)
st.set_page_config(page_title="Prediksi Energi Smart Home", layout="centered")

st.title("Prediksi Energi Rumah Tangga")
st.markdown("Aplikasi untuk memprediksi estimasi penggunaan energi peralatan rumah (Wh) berdasarkan kondisi saat ini.")
st.divider()

# 2. Input Waktu (Bisa dijadikan otomatis oleh backend nantinya)
st.subheader("Waktu & Tanggal")
col1, col2 = st.columns(2)
with col1:
    input_tanggal = st.date_input("Tanggal", datetime.today())
with col2:
    input_waktu = st.time_input("Jam", datetime.now().time())

# 3. Input Utama dari User (Sesuai skenario)
st.subheader("Kondisi Ruangan")
# Menggunakan slider agar UX lebih interaktif
suhu_ruang_utama = st.slider("Suhu Ruang Utama / T2 (°C)", min_value=15.0, max_value=35.0, value=25.0, step=0.5)
# Menggunakan number input untuk lampu
watt_lampu = st.number_input("Total Energi Lampu Menyala (Wh)", min_value=0, max_value=200, value=30, step=10)

# 4. Input Tambahan (Disembunyikan agar UI tetap rapi)
with st.expander("Kondisi Cuaca Luar (Manual/API)"):
    st.caption("Jika nantinya disambung ke API Cuaca, bagian ini bisa disembunyikan/dihapus.")
    col_cuaca1, col_cuaca2 = st.columns(2)
    with col_cuaca1:
        suhu_luar = st.number_input("Suhu Luar / T_out (°C)", value=28.0)
        kelembapan_luar = st.number_input("Kelembapan Luar / RH_out (%)", value=75.0)
        tekanan_udara = st.number_input("Tekanan Udara / Press (mmHg)", value=733.0)
    with col_cuaca2:
        kecepatan_angin = st.number_input("Kecepatan Angin (m/s)", value=5.0)
        visibilitas = st.number_input("Visibilitas (km)", value=40.0)
        titik_embun = st.number_input("Titik Embun / Tdewpoint (°C)", value=5.0)

st.divider()

# 5. Tombol Eksekusi dan Output
if st.button("Hitung Prediksi Energi", use_container_width=True):
    
    # --- BAGIAN UNTUK TEMAN BACKEND-MU ---
    # Di sini temanmu akan menyusun data_input untuk diprediksi
    data_input = pd.DataFrame({
        'T2': [suhu_ruang_utama],
        'lights': [watt_lampu],
        'T_out': [suhu_luar],
        # ... (tambahkan fitur lain sesuai kebutuhan model) ...
    })
    
    # Temanmu tinggal mengganti angka di bawah ini dengan:
    # hasil_lr = model_lr.predict(data_input)[0]
    # hasil_svr = model_svr.predict(data_input)[0]
    # hasil_rf = model_rf.predict(data_input)[0]
    
    # Simulasi hasil prediksi untuk 3 model (Angka Dummy)
    hasil_lr = 120.5 
    hasil_svr = 118.2
    hasil_rf = 125.0
    # --- AKHIR BAGIAN BACKEND ---

    # Menampilkan hasil ke layar
    st.success("Prediksi Berhasil Diproses!")
    st.markdown("### Perbandingan Hasil Prediksi Model:")
    
    # Membagi output menjadi 3 kolom berdampingan
    col_res1, col_res2, col_res3 = st.columns(3)
    
    with col_res1:
        st.metric(label="Linear Regression", value=f"{hasil_lr} Wh")
    
    with col_res2:
        st.metric(label="SVR", value=f"{hasil_svr} Wh")
        
    with col_res3:
        st.metric(label="Random Forest", value=f"{hasil_rf} Wh")
        
    st.info("Catatan: Nilai di atas masih berupa simulasi dari frontend. Model Machine Learning akan segera diintegrasikan.")
