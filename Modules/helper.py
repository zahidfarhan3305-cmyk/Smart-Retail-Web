from datetime import datetime


# ==========================================
# Format Rupiah
# ==========================================

def format_rupiah(angka):
    """
    Mengubah angka menjadi format Rupiah.

    Contoh:
    15000 -> Rp15.000
    """

    return f"Rp{angka:,.0f}".replace(",", ".")


# ==========================================
# Format Tanggal Indonesia
# ==========================================

def format_tanggal(tanggal):

    """
    Mengubah format tanggal menjadi:
    26 Juni 2026
    """

    bulan = [
        "",
        "Januari",
        "Februari",
        "Maret",
        "April",
        "Mei",
        "Juni",
        "Juli",
        "Agustus",
        "September",
        "Oktober",
        "November",
        "Desember"
    ]

    if isinstance(tanggal, str):
        tanggal = datetime.strptime(tanggal, "%Y-%m-%d")

    return f"{tanggal.day} {bulan[tanggal.month]} {tanggal.year}"


# ==========================================
# Tanggal Hari Ini
# ==========================================

def hari_ini():
    return datetime.now().strftime("%Y-%m-%d")


# ==========================================
# Jam Sekarang
# ==========================================

def jam_sekarang():
    return datetime.now().strftime("%H:%M:%S")


# ==========================================
# Nomor Transaksi
# ==========================================

def generate_nomor_transaksi(id_transaksi):

    """
    Contoh:

    id = 1

    menjadi

    TRX-20260626-0001
    """

    tanggal = datetime.now().strftime("%Y%m%d")

    return f"TRX-{tanggal}-{id_transaksi:04d}"


# ==========================================
# Hitung Subtotal
# ==========================================

def hitung_subtotal(harga, jumlah):

    return harga * jumlah


# ==========================================
# Hitung Total Keranjang
# ==========================================

def hitung_total(keranjang):

    total = 0

    for item in keranjang:
        total += item["subtotal"]

    return total


# ==========================================
# Validasi Bilangan Bulat Positif
# ==========================================

def angka_valid(nilai):

    try:

        nilai = int(nilai)

        return nilai >= 0

    except ValueError:

        return False


# ==========================================
# Validasi Harga
# ==========================================

def harga_valid(harga):

    try:

        harga = int(harga)

        return harga > 0

    except ValueError:

        return False


# ==========================================
# Validasi Nama Produk
# ==========================================

def nama_produk_valid(nama):

    return len(nama.strip()) > 0