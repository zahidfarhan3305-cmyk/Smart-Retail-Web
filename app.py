from flask import Flask, session, redirect, url_for

# Import Blueprint
from Modules.login import login_bp
from Modules.produk import produk_bp
from Modules.transaksi import transaksi_bp
from Modules.laporan import laporan_bp
from Modules.grafik import grafik_bp


# Import database
from Modules.database import buat_tabel, tambah_user_default

app = Flask(__name__)

from Modules.helper import format_rupiah

@app.context_processor
def inject_helpers():
    return dict(
        format_rupiah=format_rupiah
    )

# Secret Key untuk Session Login
app.secret_key = "smart-retail-secret-key"

# Membuat tabel database dan user default
buat_tabel()
tambah_user_default()

# Register Blueprint
app.register_blueprint(login_bp)
app.register_blueprint(produk_bp)
app.register_blueprint(transaksi_bp)
app.register_blueprint(laporan_bp)
app.register_blueprint(grafik_bp)


@app.route("/")
def home():
    if "role" not in session:
        return redirect(url_for("login.login"))

    return redirect(url_for("login.dashboard"))


@app.errorhandler(404)
def not_found(error):
    return "<h2>404 | Halaman tidak ditemukan</h2>", 404


if __name__ == "__main__":
    app.run(debug=True)

from Modules.helper import format_rupiah

app.jinja_env.globals.update(
    format_rupiah=format_rupiah
)