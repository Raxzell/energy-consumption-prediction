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
    # Di sini temanmu akan mengekstrak input_tanggal dan input_waktu 
    # menjadi fitur jam, hari, dan is_weekend.
    # Kemudian data-data ini dimasukkan ke dalam model.predict()
    
    # Contoh data yang siap dilempar ke model (sebagai DataFrame)
    data_input = pd.DataFrame({
        'T2': [suhu_ruang_utama],
        'lights': [watt_lampu],
        'T_out': [suhu_luar],
        # ... (tambahkan fitur lain sesuai kebutuhan model) ...
    })
    
    # Simulasi hasil prediksi (Ganti dengan hasil model asli)
    hasil_prediksi_dummy = 125.5 
    
    # --- AKHIR BAGIAN BACKEND ---

    # Menampilkan hasil ke layar
    st.success("Prediksi Berhasil!")
    st.metric(label="Estimasi Konsumsi Energi (Appliances)", value=f"{hasil_prediksi_dummy} Wh")
    st.info("Ini adalah tampilan awal. Nilai di atas masih berupa simulasi karena model Machine Learning belum disambungkan.")
