# Konteks proyek untuk Claude Code

Baca file ini sebelum mengerjakan apa pun di folder ini.

## Siapa saya
- Meicky Shoreamanis, dosen FIP Universitas Pelita Harapan, mahasiswa S3 Teknologi Pendidikan.
- Latar belakang saya bahasa dan sastra, **bukan programmer**. Jelaskan setiap langkah dalam bahasa Indonesia yang sangat sederhana, satu langkah per pesan, dengan analogi bila perlu.
- Laptop Windows. Perintah Python di laptop ini adalah `py` (versi 3.15.2). Ruang kerja Python ada di `.venv`. Jalankan chatbot dengan:
  `.venv\Scripts\python.exe -m streamlit run app.py`

## Tugas yang sedang dikerjakan
Proyek UAS mata kuliah **Ilmu Data dalam Pendidikan**. Instruksi dosen: *teruskan artikel UTS menjadi proyek*, dan chatbot dibuat dengan VS Code. Saya harus menyerahkan **link** chatbot yang bisa dibuka dosen.

Presentasi proyek wajib memuat 11 komponen: latar belakang, tinjauan literatur, problem framing, dataset, preprocessing, model, evaluasi, interpretasi, etika, kontribusi, dan rencana publikasi.

## Artikel UTS dan Kerangka P2I
Artikel UTS saya menyusun **Kerangka Problem-to-Impact (P2I)** untuk pengambilan keputusan berbasis data di perguruan tinggi:
1. Perumusan masalah dan keputusan
2. Pemetaan data
3. Pemeriksaan kualitas data
4. Analisis dan pemodelan, lalu **Gerbang A** (apakah model akurat, stabil, dan adil antarkelompok)
5. Protokol keputusan
6. Intervensi
7. Evaluasi dampak, lalu **Gerbang B** (apakah program bermanfaat bagi mahasiswa: lanjut, revisi, atau hentikan)

Contoh penerapan di artikel adalah **sistem peringatan dini (EWS)**: dosen PA memilih mahasiswa yang dihubungi lebih dulu pada minggu ke-6.

## Proyek UAS (sudah selesai dan sudah diuji)
1. **Notebook Colab `EWS_P2I_OULAD.ipynb`** (Tahap 1–4 dan Gerbang A), memakai data **OULAD** (Open University Learning Analytics Dataset; Kuzilek, Hlosta & Zdrahal, 2017, *Scientific Data*, 4, 170171; lisensi CC BY 4.0). Hasilnya adalah `daftar_prioritas.csv`.
2. **Chatbot "Asisten Dosen PA"** (`app.py`, Streamlit), untuk Tahap 5–6. Chatbot membaca `daftar_prioritas.csv`, menjelaskan sinyal model, menyarankan pertanyaan pembuka yang tidak menghakimi, dan mencatat keputusan dosen PA ke `log_keputusan.csv` sebagai bahan Gerbang B. Ada mode tanpa AI (berbasis aturan) dan mode Gemini (butuh `GEMINI_API_KEY` di `.env` atau di Streamlit Secrets).

Angka utama (jangan diubah tanpa menjalankan ulang notebook):
- 32.593 pendaftaran; 5.569 yang sudah mundur sebelum hari ke-42 dikeluarkan, tersisa 27.024 (43,1% gagal/mundur). Data latih angkatan 2013 (11.620), data uji angkatan 2014 (15.404).
- Kapasitas dosen PA 20% per mata kuliah. AUC / Presisi@20% / Recall@20%: aturan sederhana 0,702/0,759/0,357; regresi logistik 0,753/0,778/0,363; random forest 0,762/0,799/0,373. Batas recall maksimum sekitar 0,47 karena kapasitas.
- Audit keadilan (regresi logistik): mahasiswa disabilitas recall 0,403, FPR 0,080, proporsi gagal/mundur 0,527 (non-disabilitas 0,358 / 0,077 / 0,417); perempuan recall 0,334, FPR 0,098 (laki-laki 0,383 / 0,061).
- Sinyal terkuat: nilai tugas awal, tugas yang terlewat, aktivitas LMS minggu 5–6.

## Kaitan dengan disertasi (lewat sudut pandang, BUKAN lewat data)
- Disertasi saya: *Pengembangan Model AI-Mediated Dialogic Scaffolding (AIMS) untuk Membangun Kesadaran Kritis Calon Guru tentang Disabilitas pada Pendidikan Inklusif*. Desainnya kualitatif (studi kasus berbasis desain); datanya belum dikumpulkan.
- **Jangan memakai atau mengarang data disertasi** untuk proyek ini.
- Kaitannya ada di tiga tempat: (1) audit keadilan untuk mahasiswa penyandang disabilitas; (2) aturan chatbot yang menolak logika defisit dan menggali hambatan sistem (aksesibilitas materi, beban, perangkat); (3) laporan EWS-AIMS saya yang lama (data simulasi, mata kuliah Learning Analytics) hanya dibahas di bagian Pembahasan sebagai penerapan P2I di level kelas, dengan label jelas "data simulasi".

## Aturan kerja untukmu
- **Jangan mengubah `app.py` atau `daftar_prioritas.csv` tanpa bertanya dulu.** Angkanya sudah cocok dengan dokumen presentasi.
- Sebelum menjalankan perintah, jelaskan apa fungsinya dalam satu kalimat sederhana.
- Jangan pernah menampilkan, menyalin, atau mengunggah isi file `.env` (berisi API key).
- `CLAUDE.md` ini **jangan diunggah ke GitHub** kecuali saya setuju. Kalau baris `CLAUDE.md` belum ada di `.gitignore`, tawarkan untuk menambahkannya.
- Dosen pernah mensyaratkan kode dibuat sendiri. Bantu saya memahami kodenya supaya saya bisa menjelaskannya saat presentasi.
- Dokumen untuk diserahkan ke dosen: Word polos (hitam-putih, tanpa sampul, tanpa desain mewah).

## Langkah berikutnya (kerjakan satu per satu, tunggu saya di setiap langkah)
1. Pastikan chatbot berjalan di `http://localhost:8501` dan bisa menjawab "Mengapa mahasiswa ini ada di daftar?".
2. Unggah folder ini ke **GitHub** sebagai repository publik bernama `asisten-dosen-pa`. Yang diunggah: `app.py`, `requirements.txt`, `daftar_prioritas.csv`, `README.md`, `.gitignore`, `.env.example`. **Jangan** unggah `.env`, `.venv`, `log_keputusan.csv`, atau `CLAUDE.md`. Kalau Git belum terpasang di laptop, pakai cara unggah lewat situs GitHub (Add file > Upload files).
3. Online-kan di **Streamlit Community Cloud** (share.streamlit.io): masuk dengan akun GitHub, pilih repository, file utama `app.py`. Di *Advanced settings*, pilih Python **3.12** (jangan 3.15). Bila ingin mode Gemini, isi *Secrets* dengan `GEMINI_API_KEY = "..."`.
4. Uji link yang dihasilkan di jendela penyamaran (incognito), lalu berikan linknya kepada saya.
5. Setelah itu, bantu saya menyusun slide presentasi 11 komponen dari angka di atas.
