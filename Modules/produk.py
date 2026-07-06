from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from Modules.database import koneksi_db
from Modules.auth import admin_required
from Modules.helper import format_rupiah


# ==========================================
# Blueprint
# ==========================================

produk_bp = Blueprint(
    "produk",
    __name__,
    url_prefix="/produk"
)


# ==========================================
# Daftar Produk
# ==========================================

@produk_bp.route("/")
@admin_required
def daftar_produk():

    keyword = request.args.get(
        "keyword",
        ""
    ).strip()

    conn, cursor = koneksi_db()

    if keyword:

        cursor.execute("""
            SELECT *

            FROM produk

            WHERE nama_produk
            LIKE ?

            ORDER BY nama_produk
        """, (f"%{keyword}%",))

    else:

        cursor.execute("""
            SELECT *

            FROM produk

            ORDER BY nama_produk
        """)

    produk = cursor.fetchall()

    conn.close()

    return render_template(

        "produk.html",

        produk=produk,

        keyword=keyword,

        format_rupiah=format_rupiah

    )
# ==========================================
# Tambah Produk
# ==========================================

@produk_bp.route("/tambah", methods=["GET", "POST"])
@admin_required
def tambah_produk():

    if request.method == "POST":

        nama_produk = request.form["nama_produk"].strip()

        try:

            harga_modal = int(
                request.form["harga_modal"]
            )

            harga_jual = int(
                request.form["harga_jual"]
            )

            stok = int(
                request.form["stok"]
            )

        except ValueError:

            flash(
                "Harga dan stok harus berupa angka.",
                "danger"
            )

            return redirect(
                url_for("produk.tambah_produk")
            )

        if not nama_produk:

            flash(
                "Nama produk tidak boleh kosong.",
                "warning"
            )

            return redirect(
                url_for("produk.tambah_produk")
            )

        conn, cursor = koneksi_db()

        cursor.execute("""
            SELECT id
            FROM produk
            WHERE nama_produk = ?
        """, (nama_produk,))

        cek = cursor.fetchone()

        if cek:

            conn.close()

            flash(
                "Nama produk sudah digunakan.",
                "warning"
            )

            return redirect(
                url_for("produk.tambah_produk")
            )

        cursor.execute("""
            INSERT INTO produk
            (
                nama_produk,
                harga_modal,
                harga_jual,
                stok,
                status
            )
            VALUES
            (?,?,?,?,?)
        """,
        (
            nama_produk,
            harga_modal,
            harga_jual,
            stok,
            "Aktif"
        ))

        conn.commit()

        conn.close()

        flash(
            "Produk berhasil ditambahkan.",
            "success"
        )

        return redirect(
            url_for("produk.daftar_produk")
        )

    return render_template(
        "produk_tambah.html"
    )
# ==========================================
# Edit Produk
# ==========================================

@produk_bp.route("/edit/<int:id>", methods=["GET", "POST"])
@admin_required
def edit_produk(id):

    conn, cursor = koneksi_db()

    cursor.execute("""
        SELECT *
        FROM produk
        WHERE id = ?
    """, (id,))

    produk = cursor.fetchone()

    if not produk:

        conn.close()

        flash(
            "Produk tidak ditemukan.",
            "warning"
        )

        return redirect(
            url_for("produk.daftar_produk")
        )

    if request.method == "POST":

        nama_produk = request.form["nama_produk"].strip()

        try:

            harga_modal = int(
                request.form["harga_modal"]
            )

            harga_jual = int(
                request.form["harga_jual"]
            )

            stok = int(
                request.form["stok"]
            )

        except ValueError:

            conn.close()

            flash(
                "Harga dan stok harus berupa angka.",
                "danger"
            )

            return redirect(
                url_for(
                    "produk.edit_produk",
                    id=id
                )
            )

        cursor.execute("""
            SELECT id
            FROM produk
            WHERE nama_produk = ?
            AND id != ?
        """,
        (
            nama_produk,
            id
        ))

        cek = cursor.fetchone()

        if cek:

            conn.close()

            flash(
                "Nama produk sudah digunakan.",
                "warning"
            )

            return redirect(
                url_for(
                    "produk.edit_produk",
                    id=id
                )
            )

        cursor.execute("""
            UPDATE produk

            SET

                nama_produk = ?,

                harga_modal = ?,

                harga_jual = ?,

                stok = ?

            WHERE id = ?
        """,
        (
            nama_produk,
            harga_modal,
            harga_jual,
            stok,
            id
        ))

        conn.commit()

        conn.close()

        flash(
            "Produk berhasil diperbarui.",
            "success"
        )

        return redirect(
            url_for("produk.daftar_produk")
        )

    conn.close()

    return render_template(

        "produk_edit.html",

        produk=produk

    )
# ==========================================
# Nonaktifkan Produk
# ==========================================

@produk_bp.route("/nonaktif/<int:id>")
@admin_required
def nonaktif_produk(id):

    conn, cursor = koneksi_db()

    cursor.execute("""
        UPDATE produk
        SET status = 'Nonaktif'
        WHERE id = ?
    """, (id,))

    conn.commit()

    conn.close()

    flash(
        "Produk berhasil dinonaktifkan.",
        "success"
    )

    return redirect(
        url_for("produk.daftar_produk")
    )


# ==========================================
# Aktifkan Produk
# ==========================================

@produk_bp.route("/aktifkan/<int:id>")
@admin_required
def aktifkan_produk(id):

    conn, cursor = koneksi_db()

    cursor.execute("""
        UPDATE produk
        SET status = 'Aktif'
        WHERE id = ?
    """, (id,))

    conn.commit()

    conn.close()

    flash(
        "Produk berhasil diaktifkan kembali.",
        "success"
    )

    return redirect(
        url_for("produk.daftar_produk")
    )