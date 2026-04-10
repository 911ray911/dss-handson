from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DATASET_PATH = BASE_DIR / "dataset-dss.xlsx"
UPLOAD_FOLDER = BASE_DIR / "uploads"

CRITERIA_METADATA = {
    "Biaya Sewa (Rp/bln)": {"key": "biaya_sewa", "type": "cost"},
    "Jarak (km)": {"key": "jarak", "type": "cost"},
    "Waktu Tempuh (menit)": {"key": "waktu_tempuh", "type": "cost"},
    "Akses Jalan (jumlah)": {"key": "akses_jalan", "type": "benefit"},
    "Permintaan (unit/bln)": {"key": "permintaan", "type": "benefit"},
    "Tenaga Kerja (orang)": {"key": "tenaga_kerja", "type": "benefit"},
    "Transport (Rp/trip)": {"key": "transport", "type": "cost"},
    "Keamanan (indeks)": {"key": "keamanan", "type": "benefit"},
    "Kapasitas (m²)": {"key": "kapasitas", "type": "benefit"},
    "Ekspansi (m²)": {"key": "ekspansi", "type": "benefit"},
}

DEFAULT_WEIGHTS = {
    "biaya_sewa": 0.15,
    "jarak": 0.10,
    "waktu_tempuh": 0.10,
    "akses_jalan": 0.08,
    "permintaan": 0.15,
    "tenaga_kerja": 0.07,
    "transport": 0.10,
    "keamanan": 0.10,
    "kapasitas": 0.08,
    "ekspansi": 0.07,
}

ALTERNATIVE_COLUMN = "Lokasi"
