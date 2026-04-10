from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.utils import secure_filename

from .config import DEFAULT_WEIGHTS, UPLOAD_FOLDER
from .data_loader import DataLoadError, load_dataset
from .wsm import calculate_wsm


def register_routes(app: Flask) -> None:
    """Mendaftarkan semua endpoint web ke aplikasi Flask.

    Fungsi ini mengelompokkan seluruh route di satu tempat agar alur aplikasi
    mudah dibaca: buka halaman, upload dataset, kalkulasi, ubah bobot, lalu reset.
    """

    @app.get("/")
    def index():
        """Menyiapkan data yang dibutuhkan lalu menampilkan halaman utama.

        Halaman ini tidak selalu langsung menampilkan hasil. Jika pengguna belum
        upload dataset atau belum menekan tombol kalkulasi, halaman hanya
        menampilkan status dan petunjuk langkah berikutnya.
        """
        dataset_path = _resolve_dataset_path()
        weights = _resolve_weights()
        calculation_done = bool(session.get("calculation_done", False))
        context = _build_context(dataset_path, weights, calculation_done)
        # TUGAS: Isi nama file template HTML yang akan ditampilkan.
        # Petunjuk: lihat folder app/templates/ dan cari nama file yang sesuai.
        return render_template("???", **context)

    @app.post("/weights")
    def update_weights():
        """Menyimpan bobot baru dari form lalu menormalkannya ke total 1.

        Route ini hanya boleh dipakai setelah dataset tersedia dan kalkulasi
        pertama sudah dilakukan, supaya perubahan bobot langsung terlihat pada hasil.
        """
        if not session.get("dataset_path"):
            flash("Upload dataset terlebih dahulu sebelum mengatur bobot.", "error")
            return redirect(url_for("index"))

        if not session.get("calculation_done"):
            flash("Klik kalkulasi dulu agar perubahan bobot bisa diterapkan.", "error")
            return redirect(url_for("index"))

        # Ambil semua bobot dari form satu per satu agar bisa divalidasi.
        form_weights = {}
        try:
            for criterion_key in DEFAULT_WEIGHTS:
                raw_value = request.form.get(criterion_key, "").strip()
                if raw_value == "":
                    raise ValueError(f"Bobot untuk '{criterion_key}' wajib diisi.")
                form_weights[criterion_key] = float(raw_value)

            if any(value < 0 for value in form_weights.values()):
                raise ValueError("Bobot tidak boleh bernilai negatif.")

            total = sum(form_weights.values())
            if total <= 0:
                raise ValueError("Total bobot harus lebih besar dari 0.")

            # Semua bobot dibagi totalnya agar jumlah akhir selalu 1.
            normalized = {key: value / total for key, value in form_weights.items()}
            session["weights"] = normalized
            flash("Bobot diperbarui dan dinormalisasi otomatis.", "success")
        except ValueError as exc:
            flash(str(exc), "error")

        return redirect(url_for("index"))

    @app.post("/calculate")
    def calculate_results():
        """Menandai bahwa pengguna sudah meminta proses kalkulasi dijalankan.

        Route ini tidak menghitung hasil secara manual di dalam template.
        Ia hanya memvalidasi dataset lalu menyalakan penanda di session agar
        halaman utama boleh membangun hasil WSM.
        """
        dataset_path = _resolve_dataset_path()
        if dataset_path is None:
            flash("Upload dataset terlebih dahulu sebelum kalkulasi.", "error")
            return redirect(url_for("index"))

        try:
            load_dataset(dataset_path)
        except DataLoadError as exc:
            session.pop("dataset_path", None)
            session.pop("calculation_done", None)
            flash(f"Dataset tidak valid: {exc}", "error")
            return redirect(url_for("index"))

        session["calculation_done"] = True
        flash("Kalkulasi berhasil. Hasil WSM ditampilkan di bawah.", "success")
        return redirect(url_for("index"))

    @app.post("/upload")
    def upload_dataset():
        """Menerima file Excel dari pengguna lalu menyimpannya ke folder upload.

        Setelah file lolos validasi dasar dan isi dataset bisa dibaca, path file
        disimpan ke session. Hasil belum ditampilkan sampai pengguna klik kalkulasi.
        """
        file = request.files.get("dataset")
        if file is None or file.filename is None or file.filename.strip() == "":
            flash("Pilih file Excel terlebih dahulu.", "error")
            return redirect(url_for("index"))

        filename = secure_filename(file.filename)
        if not filename.lower().endswith((".xlsx", ".xlsm", ".xltx", ".xltm")):
            flash("File harus berformat Excel .xlsx atau turunan yang kompatibel.", "error")
            return redirect(url_for("index"))

        # Nama file dibuat aman lalu disimpan ke folder uploads.
        target_path = UPLOAD_FOLDER / filename
        file.save(target_path)

        try:
            load_dataset(target_path)
        except DataLoadError as exc:
            target_path.unlink(missing_ok=True)
            flash(f"File tidak valid: {exc}", "error")
            return redirect(url_for("index"))

        session["dataset_path"] = str(target_path)
        session["calculation_done"] = False
        flash("Dataset berhasil dimuat. Klik tombol kalkulasi untuk melihat hasil.", "success")
        return redirect(url_for("index"))

    @app.post("/reset")
    def reset_state():
        """Menghapus state session agar aplikasi kembali ke kondisi awal.

        Setelah reset, pengguna harus upload dataset lagi karena aplikasi tidak
        lagi memakai hasil atau file yang sebelumnya tersimpan di session.
        """
        session.pop("weights", None)
        session.pop("dataset_path", None)
        session.pop("calculation_done", None)
        flash("State aplikasi direset. Upload dataset lagi untuk memulai.", "success")
        return redirect(url_for("index"))


def _resolve_dataset_path() -> Path | None:
    """Mengambil path dataset aktif dari session jika file tersebut masih ada.

    Jika session belum punya dataset atau file sudah hilang dari folder upload,
    fungsi ini mengembalikan None agar halaman tahu bahwa pengguna harus upload lagi.
    """
    raw_path = session.get("dataset_path")
    if raw_path:
        candidate = Path(raw_path)
        if candidate.exists():
            return candidate
    return None


def _resolve_weights() -> dict[str, float]:
    """Mengambil bobot yang sedang aktif.

    Jika pengguna belum pernah mengubah bobot, fungsi ini mengembalikan bobot
    bawaan dari konfigurasi. Jika sudah ada di session, nilainya dipakai kembali.
    """
    session_weights = session.get("weights")
    if not session_weights:
        return DEFAULT_WEIGHTS.copy()
    return {
        key: float(session_weights.get(key, DEFAULT_WEIGHTS[key]))
        for key in DEFAULT_WEIGHTS
    }


def _build_context(
    dataset_path: Path | None, weights: dict[str, float], calculation_done: bool
) -> dict:
    """Menyusun data yang akan dikirim ke template.

    Context ini berisi semua hal yang dibutuhkan halaman HTML. Jika dataset belum
    ada atau kalkulasi belum diminta, fungsi hanya mengirim data minimum untuk
    menampilkan status. Jika kalkulasi sudah aktif, hasil WSM ikut dimasukkan.
    """
    # Ini adalah bentuk data minimal agar template tetap aman dirender.
    base_context = {
        "dataset_name": dataset_path.name if dataset_path else None,
        "dataset_path": str(dataset_path) if dataset_path else None,
        "criteria": [],
        "alternatives": [],
        "weights": weights,
        "ranking": [],
        "normalized_matrix": [],
        "contribution_matrix": [],
        "error": None,
        "calculation_done": calculation_done,
        "has_dataset": dataset_path is not None,
    }

    if dataset_path is None:
        return base_context

    if not calculation_done:
        return base_context

    try:
        # Data baru dihitung ketika pengguna sudah klik tombol kalkulasi.
        dataset = load_dataset(dataset_path)
        result = calculate_wsm(dataset, weights)
        return {
            **base_context,
            "criteria": result["criteria"],
            "alternatives": result["alternatives"],
            "weights": result["weights"],
            "ranking": result["ranking"],
            "normalized_matrix": result["normalized_matrix"],
            "contribution_matrix": result["contribution_matrix"],
        }
    except DataLoadError as exc:
        return {
            **base_context,
            "error": str(exc),
        }