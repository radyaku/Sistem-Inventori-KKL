# Sistem-Inventori-KKL

Sistem-Inventori-KKL adalah aplikasi berbasis web yang dibangun menggunakan **Django** untuk mengelola aset dan inventaris. Sistem ini mempermudah pencatatan, pemantauan, dan pembuatan laporan terkait aset yang dimiliki. 

Aplikasi ini sudah dikonfigurasi untuk berjalan di atas ekosistem **Docker**, sehingga sangat mudah untuk dijalankan di *local machine* tanpa perlu repot mengurus instalasi dependensi atau konfigurasi *environment* Python secara manual.

## Fitur Utama
*   **Manajemen Aset/Inventaris:** Pencatatan dan pengelolaan data inventaris dengan detail.
*   **Pembuatan Laporan (Reports):** Fasilitas untuk menghasilkan laporan terkait inventaris.
*   **Docker Ready:** Menjalankan *environment* pengembangan atau *deployment* secara instan.
*   **Dashboard Admin:** Disediakan secara *built-in* dari Django untuk mengelola data dengan mudah.

---

## 🚀 Cara Menjalankan untuk Pertama Kali

Pastikan kamu sudah menginstal **Docker** dan **Docker Compose** di komputermu.

1. **Clone Repositori**
   Jika kamu belum meng-clone proyek ini:
   ```bash
   git clone https://github.com/radyaku/Sistem-Inventori-KKL.git
   cd Sistem-Inventori-KKL
   ```

2. **Jalankan dengan Docker Compose**
   Cukup eksekusi perintah berikut untuk mem-build image Docker dan menjalankan *container*-nya:
   ```bash
   docker compose up -d --build
   ```
   *(Perintah di atas akan berjalan di latar belakang (background) dan mendownload dependensi yang dibutuhkan secara otomatis).*

3. **Akses Aplikasi**
   Setelah proses *build* dan inisialisasi selesai, buka *browser* kamu dan kunjungi:
   👉 **[http://localhost:8000](http://localhost:8000)**

4. **Login ke Sistem**
   Sistem secara otomatis telah membuat akun *Superuser/Admin* standar saat pertama kali dijalankan (melalui file `create_admin.py`). Silakan gunakan kredensial berikut untuk *login*:
   *   **Username / Email:** `admin` atau `admin@example.com`
   *   **Password:** `admin123`

---

## 🛠️ Catatan Teknis (Developer Notes)
*   **Port:** Aplikasi ini berjalan pada port `8000` di komputer host. Jika terjadi bentrokan port (port conflict), ubah pemetaan port di `docker-compose.yml`.
*   **Database:** Menggunakan `SQLite3` sebagai *database* bawaan yang tersimpan dalam file `db.sqlite3`.
*   **Entrypoint:** Skrip `entrypoint.sh` secara otomatis menjalankan migrasi *database*, membuat akun admin *default*, mengumpulkan *static files* Django, dan menyalakan server dengan *Gunicorn*.
*   **Pemberhentian Server:** Untuk mematikan server, jalankan perintah:
    ```bash
    docker compose down
    ```
