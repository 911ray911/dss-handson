# DSS Flask WSM

Aplikasi Python berbasis Flask untuk sistem pendukung keputusan pemilihan lokasi gudang menggunakan metode Weighted Sum Model (WSM).

## Fitur

- Wajib upload dataset Excel terlebih dahulu sebelum kalkulasi.
- Menghitung normalisasi kriteria cost dan benefit.
- Menampilkan ranking alternatif berdasarkan skor WSM.
- Override bobot dari UI dengan normalisasi otomatis.
- Upload dataset Excel baru dengan format kolom yang sama.
- Menampilkan matriks normalisasi dan kontribusi berbobot.
- UI menggunakan Tailwind CSS via CDN untuk tampilan cepat dan sederhana.

## Alur kode untuk pemula

Urutan baca yang disarankan agar cepat paham flow aplikasi:

1. Mulai dari `app.py` untuk melihat titik start server.
2. Lanjut ke `app/__init__.py` untuk memahami proses inisialisasi Flask.
3. Buka `app/route.py` karena semua endpoint HTTP ada di sini (`/`, `/weights`, `/upload`, `/reset`).
4. Lihat `app/data_loader.py` untuk proses baca dan validasi dataset Excel.
5. Terakhir baca `app/wsm.py` untuk logika normalisasi dan perhitungan ranking WSM.

Dengan urutan ini, alur request jadi lebih mudah diikuti:
request -> route handler -> data loader / WSM -> response.

Alur penggunaan aplikasi di UI:

1. Upload dataset Excel.
2. Klik tombol kalkulasi.
3. Lihat hasil ranking dan tabel analisis.

## Struktur dataset yang didukung

Dataset Excel harus memiliki satu sheet dengan kolom berikut:

- Lokasi
- Biaya Sewa (Rp/bln)
- Jarak (km)
- Waktu Tempuh (menit)
- Akses Jalan (jumlah)
- Permintaan (unit/bln)
- Tenaga Kerja (orang)
- Transport (Rp/trip)
- Keamanan (indeks)
- Kapasitas (m²)
- Ekspansi (m²)

Catatan: file `dataset-dss.xlsx` yang ada saat ini hanya berisi alternatif dan nilai kriteria. Metadata tipe kriteria dan bobot default didefinisikan di kode aplikasi pada `app/config.py`.

## Menjalankan aplikasi

```bash
source .venv/bin/activate
pip install -r requirements.txt
flask --app app.py run --debug --port 777
```

Atau:

```bash
source .venv/bin/activate
python app.py
```

Setelah server aktif, buka `http://127.0.0.1:7777`.

Rekomendasi untuk pemakaian lokal:

```bash
flask --app app.py run --debug --port 7777
```

Jika memakai `python app.py`, aplikasi juga berjalan di port `7777` sesuai konfigurasi di `app.py`.

## Asumsi WSM yang digunakan

- Kriteria cost: Biaya Sewa, Jarak, Waktu Tempuh, Transport.
- Kriteria benefit: Akses Jalan, Permintaan, Tenaga Kerja, Keamanan, Kapasitas, Ekspansi.
- Rumus normalisasi benefit: `x / max(x)`.
- Rumus normalisasi cost: `min(x) / x`.
- Skor akhir: jumlah seluruh `normalisasi * bobot`.

## Verifikasi manual

1. Jalankan aplikasi, pastikan halaman awal belum menampilkan hasil ranking.
2. Klik kalkulasi tanpa upload dan pastikan muncul pesan error arahan upload.
3. Upload file Excel valid, lalu klik kalkulasi dan pastikan hasil muncul.
4. Ubah beberapa bobot setelah kalkulasi, lalu cek ranking berubah.
5. Upload file Excel baru dan pastikan hasil lama tidak tampil sebelum kalkulasi ulang.
6. Pastikan pesan error muncul jika ada kolom wajib yang hilang.