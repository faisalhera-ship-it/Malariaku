import streamlit as st
import pandas as pd
import json
import urllib.parse
from datetime import datetime, date

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="MALARIA-YA — Puskesmas Tirta Jaya",
    page_icon="🦟",
    layout="wide"
)

# Judul Utama Dashboard
st.title("🦟 MALARIA-YA")
st.markdown("### Sistem Pengingat & Manajemen Data Pasien — Puskesmas Tirta Jaya")
st.markdown("---")

# Fungsi untuk memuat data dari file JSON di GitHub lokal (atau direktori kerja)
@st.cache_data(ttl=5) # Cache diperbarui tiap 5 detik agar data real-time
def load_data():
    try:
        with open("pasien_malaria.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return data
    except Exception as e:
        return []

data_pasien = load_data()

# Kartu Statistik Ringkasan
col1, col2, col3 = st.columns(3)

today_str = date.today().strftime("%Y-%m-%d")

total_pasien = len(data_pasien)
count_today = 0

if total_pasien > 0:
    for p in data_pasien:
        j = p.get("jadwal_reminder", {})
        if today_str in [j.get("h_1"), j.get("h_3"), j.get("h_7"), j.get("h_14"), j.get("h_28")]:
            count_today += 1

with col1:
    st.metric(label="Total Pasien Terdaftar", value=total_pasien)
with col2:
    st.metric(label="Jadwal Reminder Hari Ini", value=count_today, delta="Prioritas Utama")
with col3:
    st.metric(label="Status Sistem", value="🟢 Aktif (Streamlit & GitHub)")

st.markdown("---")

# Filter / Pencarian Data
st.subheader("📋 Daftar Pemantauan Pasien")
search_query = st.text_input("🔍 Cari berdasarkan Nama Pasien atau Alamat:", "").lower()

if total_pasien == 0:
    st.warning("Belum ada data pasien di dalam file `pasien_malaria.json`.")
else:
    # Ubah ke Pandas DataFrame untuk kemudahan filter & tampilan
    df = pd.DataFrame(data_pasien)
    
    # Filter pencarian
    if search_query:
        df = df[df['nama'].str.lower().str.contains(search_query) | df['alamat'].str.lower().str.contains(search_query)]

    if df.empty:
        st.info("Tidak ditemukan data pasien yang sesuai dengan kata kunci pencarian.")
    else:
        # Loop untuk menampilkan baris data dan tombol WA interaktif
        for index, row in df.iterrows():
            j = row.get("jadwal_reminder", {})
            status_hari = "Tidak Ada Jadwal"
            badge_color = "gray"
            
            if j.get("h_1") == today_str:
                status_hari = "Hari ke-1"
                badge_color = "red"
            elif j.get("h_3") == today_str:
                status_hari = "Hari ke-3"
                badge_color = "orange"
            elif j.get("h_7") == today_str:
                status_hari = "Hari ke-7"
                badge_color = "yellow"
            elif j.get("h_14") == today_str:
                status_hari = "Hari ke-14"
                badge_color = "blue"
            elif j.get("h_28") == today_str:
                status_hari = "Hari ke-28"
                badge_color = "green"

            # Tampilan Card per Pasien
            with st.container():
                c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
                
                with c1:
                    st.markdown(f"**👤 {row.get('nama')}** ({row.get('umur')} Th)")
                    st.markdown(f"📍 {row.get('alamat')}")
                with c2:
                    st.markdown(f"💼 **Pekerjaan:** {row.get('tempat_bekerja', '-')}")
                    st.markdown(f"✈️ **Riwayat:** {row.get('riwayat_perjalanan', '-')}")
                with c3:
                    st.markdown(f"📅 **Kunjung:** {row.get('tanggal_berkunjung')}")
                    st.markdown(f"📌 **Status Hari Ini:** :{badge_color}[**{status_hari}**]")
                with c4:
                    raw_hp = str(row.get('no_hp', '')).strip()
                    if raw_hp and raw_hp != '-':
                        formatted_hp = raw_hp.lstrip('0')
                        if not formatted_hp.startswith('62'):
                            formatted_hp = '62' + formatted_hp
                            
                        pesan_wa = (
                            f"Halo Bapak/Ibu *{row.get('nama')}*,\n\n"
                            f"Salam sehat dari *Puskesmas Tirta Jaya*.\n\n"
                            f"Ini adalah pengingat otomatis untuk jadwal minum obat / kontrol malaria Anda "
                            f"(*{status_hari}*) pada hari ini. Mohon pastikan obat dihabiskan sesuai dosis.\n\n"
                            f"Terima kasih!"
                        )
                        encoded_msg = urllib.parse.quote(pesan_wa)
                        wa_url = f"https://api.whatsapp.com/send?phone={formatted_hp}&text={encoded_msg}"
                        
                        st.markdown(f'<a href="{wa_url}" target="_blank" style="background-color:#22c55e; color:white; padding:8px 14px; border-radius:6px; text-decoration:none; font-weight:bold; display:inline-block; margin-top:10px;">💬 Kirim WA</a>', unsafe_allow_html=True)
                    else:
                        st.text("No HP Invalid")
                
                st.markdown("---")

# Catatan kaki informasi
st.markdown("<p style='text-align:center; color:gray; font-size:12px;'>© 2026 Puskesmas Tirta Jaya | Terhubung ke Google Form & GitHub</p>", unsafe_allow_html=True)
