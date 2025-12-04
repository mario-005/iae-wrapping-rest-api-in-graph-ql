# Tutorial: Modernisasi REST API dengan GraphQL Wrapper (FastAPI + Ariadne)

Tutorial ini akan memandu Anda langkah demi langkah untuk membuat "Gateway" GraphQL yang membungkus REST API yang sudah ada. Ini adalah pola yang sangat berguna ketika Anda ingin migrasi ke GraphQL tanpa harus menulis ulang seluruh backend Anda sekaligus.

Kita akan menggunakan **FastAPI** sebagai web server dan **Ariadne** untuk GraphQL, dijalankan dengan **Python 3.11**.

## Prasyarat

Pastikan Anda sudah menginstall Python 3.11 di komputer Anda.

### 1. Persiapan Lingkungan (Virtual Environment)

Agar rapi, kita akan menggunakan virtual environment (venv). Buka terminal/cmd Anda di folder ini:

**Windows:**
```powershell
# Buat venv
python -m venv venv

# Aktifkan venv
.\venv\Scripts\activate

#atau
.\.venv\Scripts\activate

```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Library

Kita butuh beberapa library (sudah ada di `requirements.txt`):
- `fastapi`: Framework web yang cepat.
- `uvicorn`: Server untuk menjalankan FastAPI.
- `ariadne`: Library GraphQL yang menggunakan pendekatan "Schema-First".
- `httpx`: HTTP client modern (support async) untuk memanggil REST API kita sendiri.

Jalankan perintah ini:
```bash
pip install -r requirements.txt
```

---

## Arsitektur

Alur kerjanya sederhana:
1. **Client** meminta data via GraphQL Query.
2. **Ariadne** menerima query tersebut.
3. **Resolver** (fungsi Python) memanggil **REST API** menggunakan `httpx`.
4. **REST API** mengembalikan JSON.
5. **Ariadne** merapikan JSON tersebut sesuai format GraphQL dan mengirimnya balik ke Client.

---

## Implementasi Kode

File `main.py` sudah disediakan di folder ini. File tersebut menggabungkan REST API (simulasi legacy) dan GraphQL Wrapper.

### Penjelasan Singkat Kode (`main.py`)

1.  **Mock Database**: Kita menggunakan list biasa sebagai database sementara.
2.  **REST API**: Endpoint `/rest/users` dan `/rest/users/{id}/posts` dibuat menggunakan FastAPI biasa.
3.  **GraphQL Schema**: Kita mendefinisikan tipe `User` yang memiliki field `posts`.
4.  **Resolvers**:
    - `resolve_users`: Mengambil data dari `/rest/users`.
    - `resolve_user_posts`: Mengambil data dari `/rest/users/{id}/posts` dan menggabungkannya ke object User. Ini adalah kunci dari "wrapping".

---

## Cara Menjalankan dan Test

1.  Jalankan aplikasi:
    ```bash
    python main.py
    ```

2.  Buka browser ke: `http://127.0.0.1:8000/graphql`

3.  Masukkan query berikut di Playground:
    ```graphql
    query {
      users {
        username
        email
        posts {
          title
        }
      }
    }
    ```

4.  **Apa yang terjadi?**
    - GraphQL mengambil daftar user dari `/rest/users`.
    - Untuk **SETIAP** user, GraphQL secara otomatis memanggil `/rest/users/{id}/posts` untuk mengambil judul postingan.
    - Hasilnya digabung menjadi satu JSON yang rapi.

---

## Menjalankan dengan Docker (Python 3.11)

File `Dockerfile` sudah disiapkan menggunakan base image `python:3.11-slim`.

### Build dan Run Docker

Buka terminal di folder project, lalu jalankan:

```bash
# 1. Build image (beri nama 'graphql-wrapper')
docker build -t graphql-wrapper .

# 2. Jalankan container
# -p 8000:8000 artinya sambungkan port 8000 komputer kita ke port 8000 container
docker run -p 8000:8000 graphql-wrapper
```

Akses kembali `http://127.0.0.1:8000/graphql` dan semuanya akan berjalan sama persis!

---

## Praktikum: Mencoba Sendiri

Sekarang saatnya Anda mencoba langsung untuk memahami alurnya.

### Bagian 1: Test Endpoint REST (Legacy)

Sebelum masuk ke GraphQL, pastikan endpoint REST berjalan dengan baik. Ini mensimulasikan pengecekan layanan lama.

1.  **Cek Daftar User**
    -   Buka browser atau Postman.
    -   Akses: `http://127.0.0.1:8000/rest/users`
    -   **Ekspektasi**: Anda melihat JSON berisi daftar user (ID 1 dan 2).

2.  **Cek Detail User**
    -   Akses: `http://127.0.0.1:8000/rest/users/1`
    -   **Ekspektasi**: JSON data user ID 1.

3.  **Cek Postingan User**
    -   Akses: `http://127.0.0.1:8000/rest/users/1/posts`
    -   **Ekspektasi**: JSON berisi daftar postingan milik user ID 1.

### Bagian 2: Test GraphQL (The Wrapper)

Sekarang kita lihat bagaimana GraphQL menyatukan data di atas.

1.  Buka `http://127.0.0.1:8000/graphql`.
2.  Jalankan query sederhana untuk mengambil nama user saja:
    ```graphql
    query {
      users {
        username
      }
    }
    ```
3.  Jalankan query kompleks (User + Posts):
    ```graphql
    query {
      user(id: 1) {
        username
        email
        posts {
          title
          content
        }
      }
    }
    ```
    Perhatikan bahwa data `posts` muncul, padahal di REST API `/rest/users/1` tidak ada data posts. Inilah tugas **Resolver** yang kita buat tadi.

### Bagian 3: Tugas Mandiri (Challenge)

Untuk memastikan pemahaman Anda, silakan kerjakan tugas berikut:

**Skenario:**
Tim backend lama baru saja menambahkan fitur "Komentar" pada setiap postingan, tapi belum ada di GraphQL.

**Tugas Anda:**
1.  Tambahkan data dummy komentar di `main.py` (misal: `comments_db`).
2.  Buat endpoint REST baru: `GET /rest/posts/{post_id}/comments`.
3.  Update Schema GraphQL: Tambahkan field `comments: [Comment]` pada tipe `Post` dan buat tipe `Comment`.
4.  Buat Resolver baru di `main.py` agar ketika kita query `Post`, komentarnya juga muncul.

**Contoh Query Target:**
```graphql
query {
  users {
    username
    posts {
      title
      comments {
        text
      }
    }
  }
}
```

Selamat mencoba!

---

## Tips Tambahan: Introspection

**Introspection** adalah fitur GraphQL yang memungkinkan kita melihat struktur schema (tipe data, query yang tersedia) secara langsung.

1.  **Via Playground**:
    -   Di halaman `http://127.0.0.1:8000/graphql`, lihat tab **"Docs"** atau **"Schema"** di sebelah kanan. Itu otomatis digenerate dari Introspection.

2.  **Via Query Manual**:
    -   Anda bisa menjalankan query khusus ini untuk melihat semua tipe yang ada:
    ```graphql
    query {
      __schema {
        types {
          name
          kind
          description
        }
      }
    }
    ```
    -   Ini sangat berguna bagi tools frontend (seperti Apollo Client) untuk mengetahui struktur API Anda secara otomatis.
