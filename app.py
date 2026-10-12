import streamlit as st
import json
import os
import urllib.parse
from datetime import date

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="MALARIA-YA — Puskesmas Tirta Jaya",
    page_icon="🦟",
    layout="wide"
)

# Nama File Database Internal di GitHub
DB_FILE = "pasien_malaria.json"

# Fungsi untuk memuat atau membuat database JSON otomatis
def load_data():
    if not os.path.exists(DB_FILE):
        # Jika file belum ada, buat file JSON baru dengan data contoh awal
        initial_data = [
            {
                "id": "MLR-1786523400000",
                "nama": "Budi Santoso",
                "umur": 34,
                "no_hp": "081234567890",
                "alamat": "RT 02 / RW 01, Desa Tirta Jaya",
                "tempat_bekerja": "Perkebunan Sawit PT Makmur",
                "riwayat_perjalanan": "Baru pulang dari Palangka Raya",
                "tanggal_berkunjung": "2026-10-12",
                "jadwal_reminder": {
                    "h_1": "2026-10-13",
                    "h_3": "2026-10-15",
                    "h_7": "2026-10-19",
                    "h_14": "2026-10-26",
                    "h_28": "2026-11-09"
                },
                "status": "Aktif"
            }
        ]
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(initial_data, f, ensure_ascii=False, indent=4)
            
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

data_pasien = load_data()
today_str = date.today().strftime("%Y-%m-%d")

# Judul Utama Dashboard
st.title("🦟 MALARIA-YA")
st.markdown("### Sistem Pengingat & Manajemen Data Pasien — Puskesmas Tirta Jaya")
st.markdown("---")

# Hitung Statistik Ringkasan
total_pasien = len(data_pasien)
count_today = 0

for p in data_pasien:
    j = p.get("jadwal_reminder", {})
    if today_str in [j.get("h_1"), j.get("h_3"), j.get("h_7"), j.get("h_14"), j.get("h_28")]:
        count_today += 1

# Tampilan Statistik
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Total Pasien Terdaftar", value=total_pasien)
with col2:
    st.metric(label="Jadwal Reminder Hari Ini", value=count_today, delta="Prioritas Utama")
with col3:
    st.metric(label="Status Sistem", value="🟢 Aktif (Single File Mode)")

st.markdown("---")

# Pencarian / Filter Pasien
st.subheader("📋 Daftar Pemantauan Pasien")
search_query = st.text_input("🔍 Cari berdasarkan Nama Pasien atau Alamat:", "").lower()

if total_pasien == 0:
    st.warning("Belum ada data pasien.")
else:
    # Filter data menggunakan list comprehension Python
    filtered_data = []
    for p in data_pasien:
        nama = str(p.get("nama", "")).lower()
        alamat = str(p.get("alamat", "")).lower()
        if search_query in nama or search_query in alamat:
            filtered_data.append(p)

    if not filtered_data:
        st.info("Tidak ditemukan data pasien yang sesuai.")
    else:
        for patient in filtered_data:
            j = patient.get("jadwal_reminder", {})
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

            # Layout Tampilan Baris Data & Tombol WA
            with st.container():
                c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
                
                with c1:
                    st.markdown(f"**👤 {patient.get('nama')}** ({patient.get('umur')} Th)")
                    st.markdown(f"📍 {patient.get('alamat')}")
                with c2:
                    st.markdown(f"💼 **Pekerjaan:** {patient.get('tempat_bekerja', '-')}")
                    st.markdown(f"✈️ **Riwayat:** {patient.get('riwayat_perjalanan', '-')}")
                with c3:
                    st.markdown(f"📅 **Kunjung:** {patient.get('tanggal_berkunjung')}")
                    st.markdown(f"📌 **Status Hari Ini:** :{badge_color}[**{status_hari}**]")
                with c4:
                    raw_hp = str(patient.get('no_hp', '')).strip()
                    if raw_hp and raw_hp != '-':
                        formatted_hp = raw_hp.lstrip('0')
                        if not formatted_hp.startswith('62'):
                            formatted_hp = '62' + formatted_hp
                            
                        pesan_wa = (
                            f"Halo Bapak/Ibu *{patient.get('nama')}*,\n\n"
                            f"Salam sehat dari *Puskesmas Tirta Jaya*.\n\n"
                            f"Ini adalah pengingat untuk jadwal minum obat / kontrol malaria Anda "
                            f"(*{status_hari}*) pada hari ini. Mohon pastikan obat dihabiskan sesuai dosis.\n\n"
                            f"Terima kasih!"
                        )
                        encoded_msg = urllib.parse.quote(pesan_wa)
                        wa_url = f"https://api.whatsapp.com/send?phone={formatted_hp}&text={encoded_msg}"
                        
                        st.markdown(f'<a href="{wa_url}" target="_blank" style="background-color:#22c55e; color:white; padding:8px 14px; border-radius:6px; text-decoration:none; font-weight:bold; display:inline-block; margin-top:10px;">💬 Kirim WA</a>', unsafe_allow_html=True)
                    else:
                        st.text("No HP Invalid")
                
                st.markdown("---")

st.markdown("<p style='text-align:center; color:gray; font-size:12px;'>© 2026 Puskesmas Tirta Jaya | MALARIA-YA Dashboard</p>", unsafe_allow_html=True)
