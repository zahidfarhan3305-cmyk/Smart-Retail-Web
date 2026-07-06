import sqlite3
import os

# ==============================
# Lokasi Database
# ==============================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "smart_retail.db")


# ==============================
# Koneksi Database
# ==============================

def koneksi_db():
    conn = sqlite3.connect(DB_PATH)

    # Menghasilkan data dalam bentuk dictionary
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    # Mengaktifkan Foreign Key SQLite
    cursor.execute("PRAGMA foreign_keys = ON")

    return conn, cursor


# ==============================
# Membuat Semua Tabel
# ==============================

def buat_tabel():

    conn, cursor = koneksi_db()

    # ==========================
    # USERS
    # ==========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        username TEXT NOT NULL UNIQUE,

        password TEXT NOT NULL,

        role TEXT NOT NULL

    )
    """)

    # ==========================
    # PRODUK
    # ==========================

    cursor.execute("""
CREATE TABLE IF NOT EXISTS produk(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    nama_produk TEXT NOT NULL,

    harga_modal INTEGER NOT NULL,

    harga_jual INTEGER NOT NULL,

    stok INTEGER NOT NULL,

    status TEXT NOT NULL DEFAULT 'Aktif',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

)
""")

    # ==========================
    # TRANSAKSI
    # ==========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transaksi(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        tanggal TEXT NOT NULL,

        total_bayar INTEGER NOT NULL,

        id_user INTEGER NOT NULL,

        FOREIGN KEY(id_user)
        REFERENCES users(id)

    )
    """)

    # ==========================
    # DETAIL TRANSAKSI
    # ==========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS detail_transaksi(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        id_transaksi INTEGER NOT NULL,

        id_produk INTEGER NOT NULL,

        jumlah INTEGER NOT NULL,

        subtotal INTEGER NOT NULL,

        FOREIGN KEY(id_transaksi)
        REFERENCES transaksi(id)
        ON DELETE CASCADE,

        FOREIGN KEY(id_produk)
        REFERENCES produk(id)

    )
    """)

    conn.commit()
    conn.close()


# ==============================
# User Default
# ==============================

def tambah_user_default():

    conn, cursor = koneksi_db()

    # Admin
    cursor.execute("""
    INSERT OR IGNORE INTO users
    (username,password,role)

    VALUES

    ('admin','admin123','admin')
    """)

    # Kasir
    cursor.execute("""
    INSERT OR IGNORE INTO users
    (username,password,role)

    VALUES

    ('kasir','kasir123','kasir')
    """)

    conn.commit()
    conn.close()