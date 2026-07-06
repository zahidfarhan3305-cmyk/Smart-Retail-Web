from flask import (
    Blueprint,
    render_template,
    request,
    Response
)

from Modules.database import koneksi_db
from Modules.auth import admin_required
from Modules.helper import (
    format_rupiah,
    format_tanggal
)

import csv
from io import StringIO


# ==========================================
# Blueprint
# ==========================================

laporan_bp = Blueprint(
    "laporan",
    __name__,
    url_prefix="/laporan"
)


# ==========================================
# Dashboard Laporan
# ==========================================

@laporan_bp.route("/")
@admin_required
def dashboard_laporan():

    conn, cursor = koneksi_db()

    # ==============================
    # Total Produk
    # ==============================

    cursor.execute("""

        SELECT COUNT(*)

        FROM produk

    """)

    total_produk = cursor.fetchone()[0]

    # ==============================
    # Total Transaksi
    # ==============================

    cursor.execute("""

        SELECT COUNT(*)

        FROM transaksi

    """)

    total_transaksi = cursor.fetchone()[0]

    # ==============================
    # Total Pendapatan
    # ==============================

    cursor.execute("""

        SELECT
            IFNULL(SUM(total_bayar),0)

        FROM transaksi

    """)

    total_pendapatan = cursor.fetchone()[0]

    conn.close()

    return render_template(

        "laporan.html",

        total_produk=total_produk,

        total_transaksi=total_transaksi,

        total_pendapatan=total_pendapatan,

        format_rupiah=format_rupiah

    )
# ==========================================
# Laporan Berdasarkan Tanggal
# ==========================================

@laporan_bp.route("/harian", methods=["GET"])
@admin_required
def laporan_harian():

    tanggal = request.args.get("tanggal")

    conn, cursor = koneksi_db()

    import os

    print("DATABASE:", os.path.abspath(conn.execute("PRAGMA database_list").fetchone()[2]))

    if tanggal:

        cursor.execute("""
            SELECT

                transaksi.id,
                transaksi.tanggal,
                transaksi.total_bayar,
                users.username

            FROM transaksi

            INNER JOIN users

                ON transaksi.id_user = users.id

            WHERE DATE(transaksi.tanggal) = DATE(?)

            ORDER BY transaksi.id DESC

        """, (tanggal,))

    else:

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

    print("Tanggal filter:", tanggal)
    print("Jumlah transaksi:", len(transaksi))

    total = sum(item["total_bayar"] for item in transaksi)

    conn.close()

    return render_template(

        "laporan_harian.html",

        transaksi=transaksi,

        tanggal=tanggal,

        total=total,

        format_rupiah=format_rupiah

    )


# ==========================================
# Laporan Bulanan
# ==========================================

@laporan_bp.route("/bulanan", methods=["GET"])
@admin_required
def laporan_bulanan():

    bulan = request.args.get("bulan")

    conn, cursor = koneksi_db()

    if bulan:

        cursor.execute("""
            SELECT

                transaksi.id,
                transaksi.tanggal,
                transaksi.total_bayar,
                users.username

            FROM transaksi

            INNER JOIN users

                ON transaksi.id_user = users.id

            WHERE strftime('%Y-%m', transaksi.tanggal)=?

            ORDER BY transaksi.id DESC

        """, (bulan,))

    else:

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

    total = sum(item["total_bayar"] for item in transaksi)

    conn.close()

    return render_template(

        "laporan_bulanan.html",

        transaksi=transaksi,

        bulan=bulan,

        total=total,

        format_rupiah=format_rupiah

    )
# ==========================================
# Export CSV
# ==========================================

@laporan_bp.route("/export/csv")
@admin_required
def export_csv():

    conn, cursor = koneksi_db()

    cursor.execute("""
        SELECT

            transaksi.id,

            transaksi.tanggal,

            users.username,

            transaksi.total_bayar,

            transaksi.uang_bayar,

            transaksi.kembalian

        FROM transaksi

        INNER JOIN users

            ON transaksi.id_user = users.id

        ORDER BY transaksi.id DESC

    """)

    data = cursor.fetchall()

    conn.close()

    output = StringIO()

    writer = csv.writer(output)

    # Header CSV
    writer.writerow([
        "ID Transaksi",
        "Tanggal",
        "Kasir",
        "Total",
        "Uang Bayar",
        "Kembalian"
    ])

    # Isi Data
    for item in data:

        writer.writerow([

            item["id"],

            item["tanggal"],

            item["username"],

            item["total_bayar"],

            item["uang_bayar"],

            item["kembalian"]

        ])

    csv_data = output.getvalue()

    output.close()

    return Response(

        csv_data,

        mimetype="text/csv",

        headers={

            "Content-Disposition":
            "attachment; filename=laporan_penjualan.csv"

        }

    )
# ==========================================
# Export CSV Harian
# ==========================================

@laporan_bp.route("/export/harian")
@admin_required
def export_harian():

    tanggal = request.args.get("tanggal")

    conn, cursor = koneksi_db()

    cursor.execute("""
        SELECT

            transaksi.id,

            transaksi.tanggal,

            users.username,

            transaksi.total_bayar

        FROM transaksi

        INNER JOIN users

            ON transaksi.id_user = users.id

        WHERE DATE(transaksi.tanggal)=DATE(?)

        ORDER BY transaksi.id DESC

    """, (tanggal,))

    data = cursor.fetchall()

    conn.close()

    output = StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "ID",
        "Tanggal",
        "Kasir",
        "Total"
    ])

    for item in data:

        writer.writerow([

            item["id"],

            item["tanggal"],

            item["username"],

            item["total_bayar"]

        ])

    return Response(

        output.getvalue(),

        mimetype="text/csv",

        headers={

            "Content-Disposition":
            f"attachment; filename=laporan_{tanggal}.csv"

        }

    )
# ==========================================
# Export CSV Bulanan
# ==========================================

@laporan_bp.route("/export/bulanan")
@admin_required
def export_bulanan():

    bulan = request.args.get("bulan")

    conn, cursor = koneksi_db()

    cursor.execute("""
        SELECT

            transaksi.id,

            transaksi.tanggal,

            users.username,

            transaksi.total_bayar

        FROM transaksi

        INNER JOIN users

            ON transaksi.id_user = users.id

        WHERE strftime('%Y-%m', transaksi.tanggal)=?

        ORDER BY transaksi.id DESC

    """, (bulan,))

    data = cursor.fetchall()

    conn.close()

    output = StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "ID",
        "Tanggal",
        "Kasir",
        "Total"
    ])

    for item in data:

        writer.writerow([

            item["id"],

            item["tanggal"],

            item["username"],

            item["total_bayar"]

        ])

    return Response(

        output.getvalue(),

        mimetype="text/csv",

        headers={

            "Content-Disposition":
            f"attachment; filename=laporan_{bulan}.csv"

        }

    )
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet


# ==========================================
# Export PDF
# ==========================================

@laporan_bp.route("/export/pdf")
@admin_required
def export_pdf():

    conn, cursor = koneksi_db()

    cursor.execute("""
        SELECT

            transaksi.id,

            transaksi.tanggal,

            users.username,

            transaksi.total_bayar

        FROM transaksi

        INNER JOIN users

            ON transaksi.id_user = users.id

        ORDER BY transaksi.id DESC

    """)

    data = cursor.fetchall()

    conn.close()

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4
    )

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph(
            "Laporan Penjualan Smart Retail",
            styles["Heading1"]
        )
    )

    tabel = [

        [
            "ID",
            "Tanggal",
            "Kasir",
            "Total"
        ]

    ]

    for item in data:

        tabel.append([

            str(item["id"]),

            item["tanggal"],

            item["username"],

            format_rupiah(
                item["total_bayar"]
            )

        ])

    table = Table(tabel)

    table.setStyle(TableStyle([

        ("BACKGROUND",(0,0),(-1,0),colors.grey),

        ("TEXTCOLOR",(0,0),(-1,0),colors.whitesmoke),

        ("GRID",(0,0),(-1,-1),1,colors.black),

        ("BACKGROUND",(0,1),(-1,-1),colors.beige),

        ("ALIGN",(0,0),(-1,-1),"CENTER"),

        ("BOTTOMPADDING",(0,0),(-1,0),8)

    ]))

    elements.append(table)

    doc.build(elements)

    pdf = buffer.getvalue()

    buffer.close()

    return Response(

        pdf,

        mimetype="application/pdf",

        headers={

            "Content-Disposition":

            "attachment; filename=laporan_penjualan.pdf"

        }

    )
# ==========================================
# Print Laporan
# ==========================================

@laporan_bp.route("/print")
@admin_required
def print_laporan():

    conn, cursor = koneksi_db()

    cursor.execute("""
        SELECT

            transaksi.id,

            transaksi.tanggal,

            users.username,

            transaksi.total_bayar

        FROM transaksi

        INNER JOIN users

            ON transaksi.id_user = users.id

        ORDER BY transaksi.id DESC
    """)

    transaksi = cursor.fetchall()

    conn.close()

    return render_template(

        "print_laporan.html",

        transaksi=transaksi,

        format_rupiah=format_rupiah

    )
# ==========================================
# Ringkasan Laporan
# ==========================================

@laporan_bp.route("/ringkasan")
@admin_required
def ringkasan():

    conn, cursor = koneksi_db()

    # ==========================================
    # Jumlah Transaksi
    # ==========================================

    cursor.execute("""
        SELECT COUNT(*)
        FROM transaksi
    """)

    jumlah_transaksi = cursor.fetchone()[0]

    # ==========================================
    # Total Pendapatan
    # ==========================================

    cursor.execute("""
        SELECT IFNULL(SUM(total_bayar), 0)
        FROM transaksi
    """)

    total = cursor.fetchone()[0]

    # ==========================================
    # Jumlah Produk
    # ==========================================

    cursor.execute("""
        SELECT COUNT(*)
        FROM produk
        WHERE status='Aktif'
    """)

    produk = cursor.fetchone()[0]

    # ==========================================
    # Total Produk Terjual
    # ==========================================

    cursor.execute("""
        SELECT IFNULL(SUM(jumlah), 0)
        FROM detail_transaksi
    """)

    total_produk_terjual = cursor.fetchone()[0]

    # ==========================================
    # Rata-rata Penjualan
    # ==========================================

    if jumlah_transaksi > 0:

        rata_rata = total / jumlah_transaksi

    else:

        rata_rata = 0

    # ==========================================
    # Top 5 Produk Terlaris
    # ==========================================

    cursor.execute("""
        SELECT

            produk.nama_produk,

            SUM(detail_transaksi.jumlah) AS jumlah_terjual,

            SUM(detail_transaksi.subtotal) AS total_penjualan

        FROM detail_transaksi

        INNER JOIN produk

            ON detail_transaksi.id_produk = produk.id

        GROUP BY produk.id

        ORDER BY jumlah_terjual DESC

        LIMIT 5
    """)

    produk_terlaris = cursor.fetchall()

    conn.close()

    return render_template(

        "ringkasan.html",

        jumlah_transaksi=jumlah_transaksi,

        total=total,

        produk=produk,

        total_produk_terjual=total_produk_terjual,

        rata_rata=rata_rata,

        produk_terlaris=produk_terlaris,

        format_rupiah=format_rupiah

    )