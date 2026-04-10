from flask import Flask

from .config import UPLOAD_FOLDER
from .route import register_routes


def create_app() -> Flask:
    """Membuat dan menyiapkan aplikasi Flask sebelum dijalankan.

    Fungsi ini adalah titik awal backend. Di sini aplikasi diberi
    konfigurasi dasar, folder upload disiapkan, lalu semua route didaftarkan.
    """
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev-secret-key"
    app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)
    UPLOAD_FOLDER.mkdir(exist_ok=True)

    register_routes(app)

    return app
