from Modules.helper import format_rupiah
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

from Modules.database import koneksi_db

# ======================================
# Blueprint Login
# ======================================

login_bp = Blueprint("login", __name__)


# ======================================
# Login
# ======================================

@login_bp.route("/login", methods=["GET", "POST"])
def login():

    # Jika sudah login langsung ke dashboard
    if "role" in session:
        return redirect(url_for("login.dashboard"))

    if request.method == "POST":

        username = request.form["username"].strip()
        password = request.form["password"].strip()

        conn, cursor = koneksi_db()

        cursor.execute("""
            SELECT *
            FROM users
            WHERE username=? AND password=?
        """, (username, password))

        user = cursor.fetchone()

        conn.close()

        if user:

            session["id_user"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]

            flash("Login berhasil.", "success")

            return redirect(url_for("login.dashboard"))

        else:

            flash("Username atau Password salah.", "danger")

    return render_template("login.html")


# ======================================
# Dashboard
# ======================================

@login_bp.route("/dashboard")
def dashboard():

    if "role" not in session:
        return redirect(url_for("login.login"))

    conn, cursor = koneksi_db()

    # Total produk
    cursor.execute("SELECT COUNT(*) AS total FROM produk")
    total_produk = cursor.fetchone()["total"]

    # Total transaksi
    cursor.execute("SELECT COUNT(*) AS total FROM transaksi")
    total_transaksi = cursor.fetchone()["total"]

    # Total pendapatan
    cursor.execute("""
        SELECT IFNULL(SUM(total_bayar),0) AS total
        FROM transaksi
    """)
    total_pendapatan = cursor.fetchone()["total"]

    conn.close()

    return render_template(
        "dashboard.html",
        username=session["username"],
        role=session["role"],
        total_produk=total_produk,
        total_transaksi=total_transaksi,
        total_pendapatan=total_pendapatan,
        format_rupiah=format_rupiah
    )


# ======================================
# Logout
# ======================================

@login_bp.route("/logout")
def logout():

    session.clear()

    flash("Anda berhasil logout.", "info")

    return redirect(url_for("login.login"))