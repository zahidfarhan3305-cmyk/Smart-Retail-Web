from functools import wraps
from flask import session, redirect, url_for, flash


# ======================================
# Wajib Login
# ======================================

def login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):

        if "id_user" not in session:

            flash("Silakan login terlebih dahulu.", "warning")
            return redirect(url_for("login.login"))

        return f(*args, **kwargs)

    return decorated_function


# ======================================
# Hanya Admin
# ======================================

def admin_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):

        if "id_user" not in session:

            flash("Silakan login terlebih dahulu.", "warning")
            return redirect(url_for("login.login"))

        if session.get("role") != "admin":

            flash("Halaman ini hanya dapat diakses Admin.", "danger")
            return redirect(url_for("login.dashboard"))

        return f(*args, **kwargs)

    return decorated_function


# ======================================
# Admin dan Kasir
# ======================================

def kasir_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):

        if "id_user" not in session:

            flash("Silakan login terlebih dahulu.", "warning")
            return redirect(url_for("login.login"))

        if session.get("role") not in ["admin", "kasir"]:

            flash("Anda tidak memiliki hak akses.", "danger")
            return redirect(url_for("login.login"))

        return f(*args, **kwargs)

    return decorated_function