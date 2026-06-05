Task Breakdown

**Task 1: Project Setup & Struktur Folder**
- Install dependency baru: `uv add supabase openpyxl`
- Buat struktur folder: `pages/`, `utils/`
- Buat `.env` dengan variabel `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `BACKEND_URL`
- Buat `utils/api.py`: fungsi `api_get(path)`, `api_post(path, data)`, `api_delete(path)` yang auto-attach `Authorization: Bearer <token>` dari `st.session_state`
- Buat `utils/auth.py`: fungsi `login(email, password)` dan `logout()` yang wrap `supabase.auth`
- **Test**: Import `utils/api.py` dan `utils/auth.py` tanpa error
- **Demo**: Struktur folder siap, dependency terinstall, helper functions bisa diimport

**Task 2: Auth Flow — Login & Logout**
- Buat `pages/login.py`: form email + password, tombol Login, error message jika gagal
- Ubah `app.py`: cek `st.session_state.get("token")` — jika tidak ada redirect ke login, jika ada tampilkan `st.navigation` dengan sidebar user info + tombol Logout
- Logout clear `session_state` dan rerun ke login
- **Test**: Kredensial salah → error ditampilkan, benar → masuk ke halaman utama, logout → kembali ke login
- **Demo**: Full login/logout flow berfungsi, halaman navigation hanya muncul setelah login

**Task 3: Modul Input Manual**
- Buat `pages/input.py` dengan `st.form`:
  - `st.date_input` untuk tanggal (field `bulan` otomatis terisi dari tanggal)
  - `st.text_input` untuk `nama_item`
  - `st.selectbox` untuk `kategori`
  - `st.number_input` untuk `quantity` (min=1) dan `harga_satuan` (min=0)
  - Preview `total_harga = quantity × harga_satuan` di bawah input sebelum submit
- Submit → `api_post("/sales", data)` → success/error message
- Di bawah form: tabel 10 record terbaru via `api_get("/sales?limit=10")`
- **Test**: Submit form kosong → validasi Streamlit mencegah submit, submit valid → record muncul di tabel bawah
- **Demo**: User input satu transaksi, klik submit, data langsung tampil di tabel

**Task 4: Modul Import Excel/CSV**
- Buat `pages/import_excel.py`:
  - `st.file_uploader` untuk `.xlsx` dan `.csv`
  - Setelah file dipilih, baca dengan Pandas dan tampilkan preview DataFrame (`st.dataframe`)
  - Validasi kolom: cek apakah semua kolom wajib ada, tampilkan pesan error jika tidak
  - Tombol "Import" → kirim file ke backend via `requests.post` multipart → tampilkan hasil (berapa record berhasil)
- **Test**: Upload file kolom benar → preview + import sukses, kolom salah → error jelas menyebutkan kolom apa yang kurang
- **Demo**: Upload file Excel sample → preview 5 baris pertama → klik Import → konfirmasi jumlah data masuk

**Task 5: Data Card View**
- Buat `pages/records.py`:
  - Sidebar filter: bulan (`st.selectbox`) dan kategori (`st.multiselect`)
  - Fetch data via `api_get("/sales?bulan=&kategori=")` sesuai filter
  - Render tiap record sebagai card menggunakan `st.columns([3,1,1,1])`: nama item + kategori | tanggal | total harga | tombol 🗑️
  - Klik hapus → `api_delete(f"/sales/{id}")` → `st.rerun()`
- **Test**: Filter bulan → hanya data bulan itu tampil, klik hapus → card hilang
- **Demo**: Semua data tampil sebagai daftar card yang bisa difilter dan dihapus satu per satu

**Task 6: Dashboard Analitik**
- Buat `pages/dashboard.py`:
  - Fetch `api_get("/sales/analytics")` sekali, parse ke DataFrame
  - **KPI row**: 3 kolom `st.metric` — Total Transaksi, Total Pendapatan, Rata-rata per Transaksi
  - **Bar chart**: Pendapatan per kategori (`st.altair_chart`)
  - **Line chart**: Trend pendapatan harian 30 hari terakhir (`st.altair_chart`)
  - **Bar chart**: Top 5 item terlaris by quantity (`st.altair_chart`)
  - Filter tahun/bulan di sidebar yang dipass sebagai query param ke endpoint
- **Test**: Tambah transaksi baru → refresh dashboard → KPI dan chart terupdate
- **Demo**: Dashboard tampil lengkap dengan 3 KPI dan 3 chart yang akurat

**Task 7: Polish & Error Handling**
- Tambah `st.spinner("Memuat data...")` di setiap fetch API
- Handle error koneksi backend: jika `requests` exception → tampilkan `st.error("Tidak dapat terhubung ke server")` bukan traceback
- Handle token expired: jika backend return 401 → auto logout dan redirect ke login
- Tambah `st.set_page_config(page_title="myRev", layout="wide")` di `app.py`
- **Test**: Matikan backend → error message muncul bukan crash, token expired → redirect ke login
- **Demo**: Aplikasi berjalan stabil end-to-end dari login hingga dashboard tanpa unhandled error
