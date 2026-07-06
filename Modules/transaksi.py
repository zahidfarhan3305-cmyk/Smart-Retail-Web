from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)

from Modules.database import koneksi_db
from Modules.auth import kasir_required
from Modules.helper import (
    format_rupiah,
    hitung_total
)

# ==========================================
# Blueprint
# ==========================================

transaksi_bp = Blueprint(
    "transaksi",
    __name__,
    url_prefix="/transaksi"
)


# ==========================================
# Inisialisasi Keranjang
# ==========================================

def inisialisasi_keranjang():

    if "keranjang" not in session:

        session["keranjang"] = []


# ==========================================
# Halaman Transaksi
# ==========================================

@transaksi_bp.route("/")
@kasir_required
def halaman_transaksi():

    inisialisasi_keranjang()

    conn, cursor = koneksi_db()

    cursor.execute("""
        SELECT *
    FROM produk
    WHERE status = 'Aktif'
    ORDER BY nama_produk
    """)

    produk = cursor.fetchall()

    conn.close()

    keranjang = session["keranjang"]

    total = hitung_total(keranjang)

    return render_template(

        "transaksi.html",

        produk=produk,

        keranjang=keranjang,

        total=total,

        format_rupiah=format_rupiah

    )
# ==========================================
# Tambah Produk ke Keranjang
# ==========================================

@transaksi_bp.route("/tambah/<int:id>", methods=["POST"])
@kasir_required
def tambah_keranjang(id):

    inisialisasi_keranjang()

    conn, cursor = koneksi_db()

    cursor.execute("""
        SELECT *
        FROM produk
        WHERE id = ?
    """, (id,))

    produk = cursor.fetchone()

    conn.close()

    if not produk:

        flash(
            "Produk tidak ditemukan.",
            "danger"
        )

        return redirect(
            url_for("transaksi.halaman_transaksi")
        )

    try:

        jumlah = int(request.form["jumlah"])

    except ValueError:

        flash(
            "Jumlah tidak valid.",
            "danger"
        )

        return redirect(
            url_for("transaksi.halaman_transaksi")
        )

    if jumlah <= 0:

        flash(
            "Jumlah harus lebih dari nol.",
            "warning"
        )

        return redirect(
            url_for("transaksi.halaman_transaksi")
        )

    keranjang = session["keranjang"]

    ditemukan = False

    for item in keranjang:

        if item["id"] == id:

            total_jumlah = item["jumlah"] + jumlah

            if total_jumlah > produk["stok"]:

                flash(
                    "Stok tidak mencukupi.",
                    "danger"
                )

                return redirect(
                    url_for("transaksi.halaman_transaksi")
                )

            item["jumlah"] = total_jumlah

            item["subtotal"] = (
                total_jumlah * item["harga"]
            )

            ditemukan = True

            break

    if not ditemukan:

        if jumlah > produk["stok"]:

            flash(
                "Stok tidak mencukupi.",
                "danger"
            )

            return redirect(
                url_for("transaksi.halaman_transaksi")
            )

        keranjang.append({

            "id": produk["id"],

            "nama": produk["nama_produk"],

            "harga": produk["harga_jual"],

            "jumlah": jumlah,

            "subtotal": (
                produk["harga_jual"] * jumlah
            )

        })

    session["keranjang"] = keranjang
    session.modified = True

    flash(
        "Produk berhasil ditambahkan ke keranjang.",
        "success"
    )

    return redirect(
        url_for("transaksi.halaman_transaksi")
    )
# ==========================================
# Tambah Jumlah Barang (+)
# ==========================================

@transaksi_bp.route("/tambah_jumlah/<int:id>", methods=["POST"])
@kasir_required
def tambah_jumlah(id):

    inisialisasi_keranjang()

    conn, cursor = koneksi_db()

    cursor.execute("""
        SELECT stok
        FROM produk
        WHERE id=?
    """, (id,))

    produk = cursor.fetchone()

    conn.close()

    if not produk:

        flash(
            "Produk tidak ditemukan.",
            "danger"
        )

        return redirect(
            url_for("transaksi.halaman_transaksi")
        )

    keranjang = session["keranjang"]

    for item in keranjang:

        if item["id"] == id:

            if item["jumlah"] + 1 > produk["stok"]:

                flash(
                    "Stok tidak mencukupi.",
                    "warning"
                )

                return redirect(
                    url_for("transaksi.halaman_transaksi")
                )

            item["jumlah"] += 1

            item["subtotal"] = (
                item["jumlah"] * item["harga"]
            )

            break

    session["keranjang"] = keranjang
    session.modified = True

    return redirect(
        url_for("transaksi.halaman_transaksi")
    )


# ==========================================
# Kurangi Jumlah Barang (-)
# ==========================================

@transaksi_bp.route("/kurang_jumlah/<int:id>", methods=["POST"])
@kasir_required
def kurang_jumlah(id):

    inisialisasi_keranjang()

    keranjang = session["keranjang"]

    for item in keranjang:

        if item["id"] == id:

            item["jumlah"] -= 1

            if item["jumlah"] <= 0:

                keranjang.remove(item)

            else:

                item["subtotal"] = (
                    item["jumlah"] * item["harga"]
                )

            break

    session["keranjang"] = keranjang
    session.modified = True

    return redirect(
        url_for("transaksi.halaman_transaksi")


    )


# ==========================================
# Hapus Satu Produk
# ==========================================

@transaksi_bp.route("/hapus/<int:id>", methods=["POST"])
@kasir_required
def hapus_item(id):

    inisialisasi_keranjang()

    keranjang = session["keranjang"]

    keranjang = [

        item

        for item in keranjang

        if item["id"] != id

    ]

    session["keranjang"] = keranjang
    session.modified = True

    flash(
        "Produk dihapus dari keranjang.",
        "info"
    )

    return redirect(
        url_for("transaksi.halaman_transaksi")
    )


# ==========================================
# Kosongkan Keranjang
# ==========================================

@transaksi_bp.route("/kosongkan", methods=["POST"])
@kasir_required
def kosongkan_keranjang():

    session["keranjang"] = []

    session.modified = True

    flash(
        "Keranjang berhasil dikosongkan.",
        "success"
    )

    return redirect(
        url_for("transaksi.halaman_transaksi")
    )
# ==========================================
# Checkout
# ==========================================

@transaksi_bp.route("/checkout", methods=["GET", "POST"])
@kasir_required
def checkout():

    inisialisasi_keranjang()

    keranjang = session["keranjang"]

    if not keranjang:

        flash(
            "Keranjang masih kosong.",
            "warning"
        )

        return redirect(
            url_for("transaksi.halaman_transaksi")
        )

    total = hitung_total(keranjang)

    if request.method == "POST":

        try:

            uang_bayar = int(
                request.form["uang_bayar"]
            )

        except ValueError:

            flash(
                "Nominal pembayaran tidak valid.",
                "danger"
            )

            return redirect(
                url_for("transaksi.checkout")
            )

        if uang_bayar < total:

            flash(
                "Uang pembayaran kurang.",
                "danger"
            )

            return redirect(
                url_for("transaksi.checkout")
            )

        kembalian = uang_bayar - total

        # Data checkout sementara
        session["checkout"] = {

            "total": total,

            "uang_bayar": uang_bayar,

            "kembalian": kembalian

        }

        session.modified = True

        return redirect(
            url_for("transaksi.simpan_transaksi")
        )

    return render_template(

        "checkout.html",

        keranjang=keranjang,

        total=total,

        format_rupiah=format_rupiah

    )
from datetime import datetime
from Modules.helper import generate_nomor_transaksi


# ==========================================
# Simpan Transaksi
# ==========================================

@transaksi_bp.route("/simpan")
@kasir_required
def simpan_transaksi():

    inisialisasi_keranjang()

    keranjang = session["keranjang"]

    if not keranjang:

        flash(
            "Keranjang kosong.",
            "warning"
        )

        return redirect(
            url_for("transaksi.halaman_transaksi")
        )

    if "checkout" not in session:

        flash(
            "Silakan lakukan proses checkout terlebih dahulu.",
            "warning"
        )

        return redirect(
            url_for("transaksi.checkout")
        )

    checkout = session["checkout"]

    total = checkout["total"]
    uang_bayar = checkout["uang_bayar"]
    kembalian = checkout["kembalian"]

    conn, cursor = koneksi_db()

    try:

        tanggal = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        id_user = session["id_user"]

        # ==================================
        # Simpan transaksi
        # ==================================

        cursor.execute("""
            INSERT INTO transaksi
            (
                tanggal,
                total_bayar,
                uang_bayar,
                kembalian,
                id_user
            )
            VALUES
            (?,?,?,?,?)
        """,
        (
            tanggal,
            total,
            uang_bayar,
            kembalian,
            id_user
        ))

        id_transaksi = cursor.lastrowid

        session["id_transaksi"] = id_transaksi

        nomor_transaksi = generate_nomor_transaksi(
            id_transaksi
        )

        # ==================================
        # Simpan detail transaksi
        # ==================================

        for item in keranjang:

            cursor.execute("""
                INSERT INTO detail_transaksi
             (
                 id_transaksi,
                id_produk,
                harga_jual,
                jumlah,
                subtotal
                )
                VALUES
                (?,?,?,?,?)
            """,
           (
             id_transaksi,
            item["id"],
            item["harga"],
            item["jumlah"],
            item["subtotal"]
            ))

            # ===============================
            # Update stok
            # ===============================

            cursor.execute("""
                UPDATE produk
                SET stok = stok - ?
                WHERE id = ?
            """,
            (
                item["jumlah"],
                item["id"]
            ))

        conn.commit()

    except Exception as e:

        conn.rollback()

        conn.close()

        flash(
            f"Terjadi kesalahan : {e}",
            "danger"
        )

        return redirect(
            url_for("transaksi.halaman_transaksi")
        )

    conn.close()

    # ==================================
    # Data Struk
    # ==================================

    session["struk"] = {

        "nomor": nomor_transaksi,

        "tanggal": tanggal,

        "kasir": session["username"],

        "keranjang": keranjang,

        "total": total,

        "uang_bayar": uang_bayar,

        "kembalian": kembalian

    }

    # Bersihkan Session

    session.pop("checkout", None)

    session["keranjang"] = []

    session.modified = True

    flash(
        "Transaksi berhasil disimpan.",
        "success"
    )

    return redirect(
        url_for("transaksi.struk")
    )
# ==========================================
# Struk Transaksi
# ==========================================

@transaksi_bp.route("/struk")
@kasir_required
def struk():

    if "id_transaksi" not in session:

        flash(
            "Struk tidak ditemukan.",
            "warning"
        )

        return redirect(
            url_for("transaksi.halaman_transaksi")
        )

    id_transaksi = session["id_transaksi"]

    conn, cursor = koneksi_db()

    # ===============================
    # Data Transaksi
    # ===============================

    cursor.execute("""
        SELECT

            transaksi.id,

            transaksi.tanggal,

            transaksi.total_bayar,

            transaksi.uang_bayar,

            transaksi.kembalian,

            users.username

        FROM transaksi

        INNER JOIN users

            ON transaksi.id_user = users.id

        WHERE transaksi.id = ?

    """, (id_transaksi,))

    transaksi = cursor.fetchone()

    if not transaksi:

        conn.close()

        flash(
            "Transaksi tidak ditemukan.",
            "warning"
        )

        return redirect(
            url_for("transaksi.halaman_transaksi")
        )

    # ===============================
    # Detail Transaksi
    # ===============================

    cursor.execute("""
        SELECT

            produk.nama_produk,

            detail_transaksi.harga_jual,

            detail_transaksi.jumlah,

            detail_transaksi.subtotal

        FROM detail_transaksi

        INNER JOIN produk

            ON detail_transaksi.id_produk = produk.id

        WHERE detail_transaksi.id_transaksi = ?

    """, (id_transaksi,))

    detail = cursor.fetchall()

    conn.close()

    return render_template(

        "struk.html",

        nomor=generate_nomor_transaksi(
            transaksi["id"]
        ),

        transaksi=transaksi,

        detail=detail,

        format_rupiah=format_rupiah

    )


# ==========================================
# Riwayat Transaksi
# ==========================================

@transaksi_bp.route("/riwayat")
@kasir_required
def riwayat_transaksi():

    conn, cursor = koneksi_db()

    cursor.execute("""
        SELECT

            transaksi.id,

            transaksi.tanggal,

            transaksi.total_bayar,

            users.username

        FROM transaksi

        INNER JOIN users

            ON transaksi.id_user = users.id

        ORDER BY transaksi.id DESC

    """)

    transaksi = cursor.fetchall()

    conn.close()

    return render_template(

        "riwayat.html",

        transaksi=transaksi,

        format_rupiah=format_rupiah

    )


# ==========================================
# Detail Transaksi
# ==========================================

@transaksi_bp.route("/detail/<int:id>")
@kasir_required
def detail_transaksi(id):

    conn, cursor = koneksi_db()

    cursor.execute("""
        SELECT

            transaksi.id,

            transaksi.tanggal,

            transaksi.total_bayar,

            transaksi.uang_bayar,

            transaksi.kembalian,

            users.username

        FROM transaksi

        INNER JOIN users

            ON transaksi.id_user = users.id

        WHERE transaksi.id = ?

    """, (id,))

    transaksi = cursor.fetchone()

    if not transaksi:

        conn.close()

        flash(
            "Transaksi tidak ditemukan.",
            "warning"
        )

        return redirect(
            url_for("transaksi.riwayat_transaksi")
        )

    cursor.execute("""
        SELECT

            produk.nama_produk,

            detail_transaksi.harga_jual,

            detail_transaksi.jumlah,

            detail_transaksi.subtotal

        FROM detail_transaksi

        INNER JOIN produk

            ON detail_transaksi.id_produk = produk.id

        WHERE detail_transaksi.id_transaksi = ?

    """, (id,))

    detail = cursor.fetchall()

    conn.close()

    return render_template(

        "detail_transaksi.html",

        transaksi=transaksi,

        detail=detail,

        nomor=generate_nomor_transaksi(id),

        format_rupiah=format_rupiah

    )


# ==========================================
# Cetak Ulang Struk
# ==========================================

@transaksi_bp.route("/cetak/<int:id>")
@kasir_required
def cetak_struk(id):

    conn, cursor = koneksi_db()

    cursor.execute("""
        SELECT

            transaksi.id,

            transaksi.tanggal,

            transaksi.total_bayar,

            transaksi.uang_bayar,

            transaksi.kembalian,

            users.username

        FROM transaksi

        INNER JOIN users

            ON transaksi.id_user = users.id

        WHERE transaksi.id = ?

    """, (id,))

    transaksi = cursor.fetchone()

    if not transaksi:

        conn.close()

        flash(
            "Transaksi tidak ditemukan.",
            "warning"
        )

        return redirect(
            url_for("transaksi.riwayat_transaksi")
        )

    cursor.execute("""
        SELECT

            produk.nama_produk,

            detail_transaksi.harga_jual,

            detail_transaksi.jumlah,

            detail_transaksi.subtotal

        FROM detail_transaksi

        INNER JOIN produk

            ON detail_transaksi.id_produk = produk.id

        WHERE detail_transaksi.id_transaksi = ?

    """, (id,))

    detail = cursor.fetchall()

    conn.close()

    return render_template(

        "struk.html",

        nomor=generate_nomor_transaksi(id),

        transaksi=transaksi,

        detail=detail,

        format_rupiah=format_rupiah

    )