"""
Asisten Dosen PA: chatbot untuk Sistem Peringatan Dini (Kerangka P2I, Tahap 5-6)
Proyek UAS Ilmu Data dalam Pendidikan - Meicky Shoreamanis

Cara menjalankan (di terminal VS Code):
    streamlit run app.py

Chatbot ini membaca file daftar_prioritas.csv (hasil notebook Colab),
lalu membantu dosen PA:
  1. memahami MENGAPA seorang mahasiswa ada di urutan atas,
  2. menyiapkan pertanyaan pembuka percakapan,
  3. memilih bentuk pendampingan,
  4. mencatat keputusan (data untuk evaluasi dampak / Gerbang B).

Keputusan tetap di tangan dosen PA. Chatbot tidak memberi label "berisiko".
"""

import os
from datetime import datetime

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()  # membaca GEMINI_API_KEY dan GEMINI_MODEL dari file .env (kalau ada)

FILE_DAFTAR = "daftar_prioritas.csv"
FILE_LOG = "log_keputusan.csv"
def ambil_rahasia(nama, bawaan=""):
    """Ambil API key dari file .env (di laptop) atau dari Secrets (di Streamlit Cloud)."""
    nilai = os.getenv(nama, "")
    if not nilai:
        try:
            nilai = st.secrets.get(nama, "")
        except Exception:  # tidak ada file secrets, misalnya saat dijalankan di laptop
            nilai = ""
    return (nilai or bawaan).strip()


API_KEY = ambil_rahasia("GEMINI_API_KEY")
MODEL_GEMINI = ambil_rahasia("GEMINI_MODEL", "gemini-2.5-flash")

# ----------------------------------------------------------------------
# 1. Aturan perilaku chatbot (system prompt). Inilah "etika" yang ditanam.
# ----------------------------------------------------------------------
ATURAN = """Kamu adalah Asisten Dosen Pembimbing Akademik (PA) di sebuah perguruan tinggi di Indonesia.
Tugasmu membantu dosen PA menyiapkan percakapan pendampingan dengan mahasiswa.

Aturan yang WAJIB kamu ikuti:
1. Pakai hanya data mahasiswa yang diberikan. Jangan mengarang fakta tentang mahasiswa.
2. Petunjuk dari model adalah SINYAL, bukan diagnosis dan bukan sebab. Selalu katakan bahwa
   penyebab sebenarnya baru bisa diketahui lewat percakapan.
3. Jangan pernah memakai label yang menghakimi seperti "berisiko", "malas", "lemah", "bermasalah",
   atau "tidak mampu". Sebut "mahasiswa dalam daftar prioritas pendampingan".
4. Saat menyarankan pertanyaan, pakai pertanyaan terbuka yang menggali HAMBATAN, termasuk hambatan
   di luar diri mahasiswa: beban kerja atau kuliah lain, akses internet dan perangkat, tanggung jawab
   keluarga, kesehatan, kejelasan instruksi tugas, dan aksesibilitas materi (misalnya bagi mahasiswa
   penyandang disabilitas). Jangan hanya mencari kekurangan pada mahasiswa.
5. Pilihan tindak lanjut yang boleh kamu sarankan: percakapan pendampingan, tutor sebaya,
   penyesuaian/akomodasi belajar bersama dosen pengampu, atau rujukan ke layanan konseling
   atau unit layanan disabilitas. Jangan menyarankan sanksi.
6. Keputusan akhir selalu milik dosen PA. Ingatkan bila dosen tampak menyerahkan keputusan kepadamu.
7. Jangan menanyakan atau menebak gender, disabilitas, agama, suku, atau kondisi ekonomi mahasiswa.
8. Jawab dalam bahasa Indonesia yang hangat, singkat (maksimal 200 kata), dan praktis.
"""

PILIHAN_TINDAKAN = [
    "Hubungi untuk percakapan pendampingan",
    "Tawarkan tutor sebaya",
    "Diskusikan akomodasi dengan dosen pengampu",
    "Rujuk ke konseling / unit layanan disabilitas",
    "Pantau dulu, belum perlu dihubungi",
]


# ----------------------------------------------------------------------
# 2. Memuat data
# ----------------------------------------------------------------------
@st.cache_data
def muat_daftar(sumber):
    return pd.read_csv(sumber)


def profil_teks(m):
    """Ubah satu baris data mahasiswa menjadi teks yang bisa dibaca chatbot."""
    return (
        f"Kode mahasiswa: {m['kode']}\n"
        f"Status di daftar: {m['prioritas']} (urutan berdasarkan skor model {m['skor_prioritas']})\n"
        f"Petunjuk model: {m['petunjuk']}\n"
        f"Hari aktif di LMS (minggu 1-6): {int(m['hari_aktif'])} hari\n"
        f"Klik LMS sebelum kuliah: {int(m['klik_pra_kuliah'])}; minggu 1-4: {int(m['klik_minggu_1_4'])}; "
        f"minggu 5-6: {int(m['klik_minggu_5_6'])}\n"
        f"Tugas jatuh tempo: {int(m['tugas_jatuh_tempo'])}; dikumpulkan: {int(m['tugas_dikumpulkan'])}; "
        f"terlewat: {int(m['tugas_terlewat'])}; terlambat: {int(m['tugas_terlambat'])}\n"
        f"Nilai rata-rata tugas awal: {m['nilai_rata2']}\n"
        f"Beban studi: {int(m['studied_credits'])} kredit; pernah mengulang: {int(m['num_of_prev_attempts'])} kali"
    )


# ----------------------------------------------------------------------
# 3. Mode tanpa AI: jawaban berbasis aturan (bisa dipakai tanpa API key)
# ----------------------------------------------------------------------
def jawab_tanpa_ai(pesan, m):
    p = pesan.lower()
    if any(k in p for k in ["kenapa", "mengapa", "alasan", "sebab", "petunjuk"]):
        return (
            f"**{m['kode']}** ada di urutan ini karena model melihat sinyal berikut: "
            f"**{m['petunjuk']}**.\n\n"
            f"Datanya: {int(m['hari_aktif'])} hari aktif di LMS, {int(m['klik_minggu_5_6'])} klik di minggu 5-6, "
            f"{int(m['tugas_terlewat'])} tugas terlewat, nilai rata-rata {m['nilai_rata2']}.\n\n"
            "Ingat: ini sinyal, bukan sebab. Penyebabnya baru bisa diketahui lewat percakapan."
        )
    if any(k in p for k in ["tanya", "pertanyaan", "membuka", "mulai", "bicara", "ngobrol"]):
        return (
            "Beberapa pertanyaan pembuka yang tidak menghakimi:\n"
            "1. \"Bagaimana minggu-minggu pertama kuliahmu sejauh ini?\"\n"
            "2. \"Apa yang paling menyita waktumu belakangan ini, di kampus atau di luar kampus?\"\n"
            "3. \"Apakah instruksi tugas dan materi di LMS mudah kamu akses dan pahami?\"\n"
            "4. \"Adakah yang bisa kampus ubah supaya kamu lebih mudah mengikuti kuliah ini?\"\n\n"
            "Pertanyaan ke-3 dan ke-4 menggali hambatan dari sisi sistem, bukan hanya dari sisi mahasiswa."
        )
    if any(k in p for k in ["intervensi", "lakukan", "bantu", "saran", "tindak"]):
        return (
            "Pilihan tindak lanjut (Anda yang memutuskan):\n"
            "- **Percakapan pendampingan** untuk memahami hambatannya.\n"
            "- **Tutor sebaya** bila hambatannya terkait pemahaman materi.\n"
            "- **Akomodasi bersama dosen pengampu** bila hambatannya terkait akses materi atau tenggat.\n"
            "- **Rujukan ke konseling / unit layanan disabilitas** bila ada kebutuhan di luar akademik.\n\n"
            "Catat keputusan Anda di panel kiri supaya dampaknya bisa dievaluasi nanti."
        )
    return (
        "Saya bisa membantu tiga hal. Coba ketik:\n"
        "- \"**Mengapa** mahasiswa ini ada di daftar?\"\n"
        "- \"**Pertanyaan** apa untuk membuka percakapan?\"\n"
        "- \"**Saran** tindak lanjut?\""
    )


# ----------------------------------------------------------------------
# 4. Mode Gemini: jawaban dari model bahasa (perlu API key di file .env)
# ----------------------------------------------------------------------
def jawab_gemini(riwayat, m):
    from google import genai
    from google.genai import types

    klien = genai.Client(api_key=API_KEY)
    isi = [
        types.Content(role="user" if r["role"] == "user" else "model",
                      parts=[types.Part(text=r["content"])])
        for r in riwayat
    ]
    konfigurasi = types.GenerateContentConfig(
        system_instruction=ATURAN + "\n\nData mahasiswa yang sedang dibahas:\n" + profil_teks(m),
        temperature=0.4,
    )
    jawaban = klien.models.generate_content(model=MODEL_GEMINI, contents=isi, config=konfigurasi)
    return jawaban.text


# ----------------------------------------------------------------------
# 5. Tampilan (Streamlit)
# ----------------------------------------------------------------------
st.set_page_config(page_title="Asisten Dosen PA", page_icon="🎓", layout="wide")
st.title("Asisten Dosen PA")
st.caption("Sistem peringatan dini minggu ke-6 | Kerangka P2I, Tahap 5-6 | Keputusan tetap di tangan dosen PA")

with st.sidebar:
    st.header("1. Data")
    unggahan = st.file_uploader("Unggah daftar_prioritas.csv (opsional)", type="csv")
    if unggahan is not None:
        daftar = muat_daftar(unggahan)
    elif os.path.exists(FILE_DAFTAR):
        daftar = muat_daftar(FILE_DAFTAR)
    else:
        st.error("File daftar_prioritas.csv belum ada. Salin dari Colab ke folder ini.")
        st.stop()

    hanya_prioritas = st.checkbox("Tampilkan hanya 'Hubungi minggu ini'", value=True)
    tampil = daftar[daftar["prioritas"] == "Hubungi minggu ini"] if hanya_prioritas else daftar
    kode = st.selectbox("2. Pilih mahasiswa", tampil["kode"].tolist())
    m = daftar[daftar["kode"] == kode].iloc[0]

    st.header("3. Mode chatbot")
    pakai_ai = st.toggle("Pakai Gemini", value=bool(API_KEY), disabled=not API_KEY)
    if not API_KEY:
        st.caption("Belum ada GEMINI_API_KEY di file .env, jadi chatbot memakai mode tanpa AI.")

    st.header("4. Catat keputusan")
    tindakan = st.selectbox("Tindakan yang Anda pilih", PILIHAN_TINDAKAN)
    catatan = st.text_area("Catatan singkat (opsional)")
    if st.button("Simpan keputusan"):
        baris = pd.DataFrame([{
            "waktu": datetime.now().isoformat(timespec="seconds"),
            "kode": m["kode"], "prioritas": m["prioritas"],
            "skor_prioritas": m["skor_prioritas"], "tindakan": tindakan, "catatan": catatan,
        }])
        baris.to_csv(FILE_LOG, mode="a", header=not os.path.exists(FILE_LOG), index=False)
        st.success("Tersimpan di log_keputusan.csv")

# Kartu ringkas mahasiswa
kiri, tengah, kanan = st.columns(3)
kiri.metric("Hari aktif di LMS (minggu 1-6)", int(m["hari_aktif"]))
tengah.metric("Klik LMS minggu 5-6", int(m["klik_minggu_5_6"]))
kanan.metric("Tugas terlewat", f"{int(m['tugas_terlewat'])} dari {int(m['tugas_jatuh_tempo'])}")
st.info(f"**Sinyal dari model:** {m['petunjuk']}  \n"
        "Ini bahan percakapan, bukan diagnosis.")

# Riwayat percakapan disimpan per mahasiswa
if "riwayat" not in st.session_state or st.session_state.get("kode_aktif") != kode:
    st.session_state.riwayat = []
    st.session_state.kode_aktif = kode

for r in st.session_state.riwayat:
    with st.chat_message(r["role"]):
        st.markdown(r["content"])

pesan = st.chat_input("Tanyakan sesuatu tentang mahasiswa ini...")
if pesan:
    st.session_state.riwayat.append({"role": "user", "content": pesan})
    with st.chat_message("user"):
        st.markdown(pesan)
    with st.chat_message("assistant"):
        try:
            jawaban = jawab_gemini(st.session_state.riwayat, m) if pakai_ai else jawab_tanpa_ai(pesan, m)
        except Exception as e:  # misalnya API key salah atau internet putus
            jawaban = (f"Gemini tidak bisa dihubungi ({e}). Jawaban mode tanpa AI:\n\n"
                       + jawab_tanpa_ai(pesan, m))
        st.markdown(jawaban)
    st.session_state.riwayat.append({"role": "assistant", "content": jawaban})
