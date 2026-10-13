import streamlit as st
import json
import os
import requests
import urllib.parse
from datetime import date, datetime, timedelta

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="MALARIA-YA — Puskesmas Tirta Jaya",
    page_icon="🦟",
    layout="wide"
)

DB_FILE = "pasien_malaria.json"
GOOGLE_APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwtIFK6lc1aTu_fp6l2lod5KQJBljeiYaVnwXfoz1xiOuvCUsdkZlqsab-TpnFWcEuT/exec"

# Fungsi aman untuk memuat atau membuat database JSON lokal
def load_data():
    try:
        if not os.path.exists(DB_FILE):
            initial_data = [
                {
                    "id": "MLR-1786523400000",
                    "nama": "Budi Santoso",
                    "umur": 34,
                    "no_hp": "081234567890",
                    "alamat": "RT 02 / RW 01, Desa Tirta Jaya",
                    "tempat_bekerja": "Perkebunan Sawit PT Makmur",
                    "riwayat_perjalanan": "Baru pulang dari Palangka Raya",
                    "diagnosa": "Malaria Falciparum",
                    "pengobatan": "DHP + Primakuin",
                    "tanggal_berkunjung": "2026-10-12",
                    "jadwal_reminder": {
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
                
        with open(DB_FILE, "r", encoding="utf-8") as f:
            content = f.read()
            if not content.strip():
                return []
            return json.loads(content)
    except Exception:
        return []

# Fungsi untuk menyimpan data lokal JSON
def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Fungsi kirim data ke Google Apps Script (Webhook ke Google Sheets)
def sync_to_google_sheets(payload):
    try:
        response = requests.post(GOOGLE_APPS_SCRIPT_URL, json=payload, timeout=10)
        return response.status_code == 200
    except Exception:
        return False

# Hitung jadwal kontrol Hari ke-3, 7, 14, 28
def hitung_jadwal_kontrol(tgl_kunjung):
    base_date = datetime.strptime(tgl_kunjung, "%Y-%m-%d").date()
    return {
        "h_3": str(base_date + timedelta(days=3)),
        "h_7": str(base_date + timedelta(days=7)),
        "h_14": str(base_date + timedelta(days=14)),
        "h_28": str(base_date + timedelta(days=28))
    }

data_pasien = load_data()
today_str = date.today().strftime("%Y-%m-%d")

# Judul Utama Dashboard
st.title("🦟 MALARIA-YA")
st.markdown("### Sistem Pengingat, Pengobatan & Manajemen Data Pasien — Puskesmas Tirta Jaya")
st.markdown("---")

# Sidebar untuk Input Data
with st.sidebar:
    st.header("📥 Input Data Pasien Baru")
    st.markdown("Klik **Save** untuk menyimpan data ke dashboard sekaligus merekamnya ke Google Sheets.")
    
    with st.form("form_tambah_pasien"):
        f_nama = st.text_input("Nama Lengkap Pasien")
        f_umur = st.number_input("Umur (Tahun)", min_value=1, max_value=120, value=30)
        f_hp = st.text_input("Nomor WhatsApp (Contoh: 0812...)")
        f_alamat = st.text_area("Alamat Lengkap")
        f_kerja = st.text_input("Tempat Bekerja")
        f_riwayat = st.text_input("Riwayat Perjalanan (1 Bulan Terakhir)")
        f_diagnosa = st.selectbox("Diagnosa Medis", ["Malaria Falciparum", "Malaria Vivax", "Malaria Mixed", "Malaria Ovale/Malariae"])
        f_pengobatan = st.text_input("Pengobatan", value="DHP + Primakuin")
        f_tgl = st.date_input("Tanggal Berkunjung / Hari ke-1", value=date.today())
        
        submit_btn = st.form_submit_button("💾 Save ke Dashboard & Google Sheets")
        
        if submit_btn:
            if f_nama and f_hp and f_alamat:
                tgl_str = str(f_tgl)
                newItem = {
                    "id": "MLR-" + str(int(datetime.now().timestamp() * 1000)),
                    "nama": f_nama,
                    "umur": int(f_umur),
                    "no_hp": f_hp,
                    "alamat": f_alamat,
                    "tempat_bekerja": f_kerja,
                    "riwayat_perjalanan": f_riwayat,
                    "diagnosa": f_diagnosa,
                    "pengobatan": f_pengobatan,
                    "tanggal_berkunjung": tgl_str,
                    "jadwal_reminder": hitung_jadwal_kontrol(tgl_str),
                    "status": "Aktif"
                }
                
                # Simpan lokal
                data_pasien.append(newItem)
                save_data(data_pasien)
                
                # Sinkronisasi otomatis ke Google Sheets via Web App
                sync_success = sync_to_google_sheets(newItem)
                
                if sync_success:
                    st.success(f"Data pasien **{f_nama}** berhasil disave & masuk ke Google Sheets!")
                else:
                    st.warning(f"Data pasien **{f_nama}** tersimpan di dashboard lokal (Gagal sync ke Google Sheets).")
                
                st.rerun()
            else:
                st.error("Mohon isi minimal Nama, No HP, dan Alamat.")

# Hitung Statistik Ringkasan
total_pasien = len(data_pasien)
count_today = 0

for p in data_pasien:
    j = p.get("jadwal_reminder", {})
    if today_str in [j.get("h_3"), j.get("h_7"), j.get("h_14"), j.get("h_28")]:
        count_today += 1

# Tampilan Statistik
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Total Pasien Terdaftar", value=total_pasien)
with col2:
    st.metric(label="Jadwal Kontrol Hari Ini", value=count_today, delta="Prioritas Utama")
with col3:
    st.metric(label="Status Sistem", value="🟢 Terhubung ke Google Sheets")

st.markdown("---")

# Pencarian / Filter Pasien
st.subheader("📋 Daftar Pemantauan & Status Pengobatan Pasien")
search_query = st.text_input("🔍 Cari berdasarkan Nama Pasien atau Alamat:", "").lower()

if total_pasien == 0:
    st.warning("Belum ada data pasien terdaftar.")
else:
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
            status_hari = "Tidak Ada Jadwal Kontrol Hari Ini"
            badge_color = "gray"
            
            if j.get("h_3") == today_str:
                status_hari = "Kontrol Hari ke-3"
                badge_color = "orange"
            elif j.get("h_7") == today_str:
                status_hari = "Kontrol Hari ke-7"
                badge_color = "yellow"
            elif j.get("h_14") == today_str:
                status_hari = "Kontrol Hari ke-14"
                badge_color = "blue"
            elif j.get("h_28") == today_str:
                status_hari = "Kontrol Hari ke-28"
                badge_color = "green"

            with st.container():
                c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
                
                with c1:
                    st.markdown(f"**👤 {patient.get('nama')}** ({patient.get('umur')} Th)")
                    st.markdown(f"📍 {patient.get('alamat')}")
                    st.markdown(f"🩺 **Diagnosa:** `{patient.get('diagnosa', 'Malaria Falciparum')}`")
                with c2:
                    st.markdown(f"💊 **Pengobatan:** `{patient.get('pengobatan', 'DHP + Primakuin')}`")
                    st.markdown(f"💼 **Pekerjaan:** {patient.get('tempat_bekerja', '-')}")
                    st.markdown(f"✈️ **Riwayat:** {patient.get('riwayat_perjalanan', '-')}")
                with c3:
                    st.markdown(f"📅 **Tgl Kunjung (H-1):** {patient.get('tanggal_berkunjung')}")
                    st.markdown(f"📌 **Status Hari Ini:** :{badge_color}[**{status_hari}**]")
                    st.markdown(f"<small>Jadwal Kontrol: H3: {j.get('h_3')} | H7: {j.get('h_7')} | H14: {j.get('h_14')} | H28: {j.get('h_28')}</small>", unsafe_allow_html=True)
                with c4:
                    raw_hp = str(patient.get('no_hp', '')).strip()
                    if raw_hp and raw_hp != '-':
                        formatted_hp = raw_hp.lstrip('0')
                        if not formatted_hp.startswith('62'):
                            formatted_hp = '62' + formatted_hp
                            
                        pesan_wa = (
                            f"Halo Bapak/Ibu *{patient.get('nama')}*,\n\n"
                            f"Salam sehat dari *Puskesmas Tirta Jaya*.\n\n"
                            f"Ini adalah pengingat untuk jadwal kontrol & evaluasi pengobatan malaria Anda "
                            f"(*{status_hari}*) pada hari ini.\n\n"
                            f"Pastikan obat DHP dan Primakuin diminum teratur sesuai anjuran. Terima kasih!"
                        )
                        encoded_msg = urllib.parse.quote(pesan_wa)
                        wa_url = f"https://api.whatsapp.com/send?phone={formatted_hp}&text={encoded_msg}"
                        
                        st.markdown(f'<a href="{wa_url}" target="_blank" style="background-color:#22c55e; color:white; padding:8px 14px; border-radius:6px; text-decoration:none; font-weight:bold; display:inline-block; margin-top:10px;">💬 Kirim WA</a>', unsafe_allow_html=True)
                    else:
                        st.text("No HP Invalid")
                
                st.markdown("---")

st.markdown("<p style='text-align:center; color:gray; font-size:12px;'>© 2026 Puskesmas Tirta Jaya | MALARIA-YA Dashboard</p>", unsafe_allow_html=True)
