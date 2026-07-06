import io

from flask import (
    Blueprint,
    render_template,
    request,
    send_file
)

from matplotlib.figure import Figure

from Modules.database import koneksi_db
from Modules.auth import admin_required


# ==========================================
# Blueprint
# ==========================================

grafik_bp = Blueprint(
    "grafik",
    __name__,
    url_prefix="/grafik"
)


# ==========================================
# Dashboard Grafik
# ==========================================

@grafik_bp.route("/")
@admin_required
def dashboard_grafik():

    tahun = request.args.get("tahun")

    return render_template(
        "grafik.html",
        tahun=tahun
    )


# ==========================================
# Grafik Pendapatan Bulanan
# ==========================================

@grafik_bp.route("/pendapatan-bulanan")
@admin_required
def grafik_bulanan():

    tahun = request.args.get("tahun")

    conn, cursor = koneksi_db()

    if tahun:

        cursor.execute("""
            SELECT

                strftime('%m', tanggal) AS bulan,

                SUM(total_bayar) AS total

            FROM transaksi

            WHERE strftime('%Y', tanggal)=?

            GROUP BY bulan

            ORDER BY bulan
        """, (tahun,))

    else:

        cursor.execute("""
            SELECT

                strftime('%m', tanggal) AS bulan,

                SUM(total_bayar) AS total

            FROM transaksi

            GROUP BY bulan

            ORDER BY bulan
        """)

    data = cursor.fetchall()

    conn.close()

    nama_bulan = [
        "Jan","Feb","Mar","Apr","Mei","Jun",
        "Jul","Agu","Sep","Okt","Nov","Des"
    ]

    bulan = []
    total = []

    for item in data:

        bulan.append(
            nama_bulan[int(item["bulan"]) - 1]
        )

        total.append(
            item["total"]
        )

    fig = Figure(figsize=(10,5))

    ax = fig.add_subplot(111)

    ax.bar(
        bulan,
        total
    )

    ax.set_title("Pendapatan Bulanan")

    ax.set_xlabel("Bulan")

    ax.set_ylabel("Pendapatan (Rp)")

    fig.tight_layout()

    image = io.BytesIO()

    fig.savefig(
        image,
        format="png"
    )

    image.seek(0)

    return send_file(
        image,
        mimetype="image/png"
    )
# ==========================================
# Grafik Pendapatan Harian
# ==========================================

@grafik_bp.route("/pendapatan-harian")
@admin_required
def grafik_harian():

    tahun = request.args.get("tahun")

    bulan = request.args.get("bulan")

    conn, cursor = koneksi_db()

    if tahun and bulan:

        cursor.execute("""
            SELECT

                strftime('%d', tanggal) AS hari,

                SUM(total_bayar) AS total

            FROM transaksi

            WHERE strftime('%Y', tanggal)=?
            AND strftime('%m', tanggal)=?

            GROUP BY hari

            ORDER BY hari
        """, (tahun, bulan.zfill(2)))

    else:

        cursor.execute("""
            SELECT

                strftime('%d', tanggal) AS hari,

                SUM(total_bayar) AS total

            FROM transaksi

            GROUP BY hari

            ORDER BY hari
        """)

    data = cursor.fetchall()

    conn.close()

    hari = []
    total = []

    for item in data:

        hari.append(item["hari"])

        total.append(item["total"])

    fig = Figure(figsize=(10,5))

    ax = fig.add_subplot(111)

    ax.plot(
        hari,
        total,
        marker="o",
        linewidth=2
    )

    ax.set_title("Pendapatan Harian")

    ax.set_xlabel("Tanggal")

    ax.set_ylabel("Pendapatan (Rp)")

    ax.grid(True)

    fig.tight_layout()

    image = io.BytesIO()

    fig.savefig(
        image,
        format="png"
    )

    image.seek(0)

    return send_file(
        image,
        mimetype="image/png"
    )