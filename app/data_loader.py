from pathlib import Path

import pandas as pd

from .config import ALTERNATIVE_COLUMN, CRITERIA_METADATA


class DataLoadError(Exception):
    """Menandai bahwa dataset tidak bisa dibaca atau isinya tidak sesuai aturan."""

    pass


def load_dataset(file_path: Path) -> dict:
    """Membaca file Excel lalu mengubahnya menjadi format data yang dipakai aplikasi.

    Fungsi ini memastikan file bisa dibuka, kolom wajib tersedia, dan semua nilai
    kriteria berisi angka. Hasil akhirnya berupa dictionary berisi daftar kriteria
    dan daftar alternatif yang siap dipakai oleh proses WSM.
    """
    try:
        dataframe = pd.read_excel(file_path)
    except Exception as exc:
        raise DataLoadError("Workbook Excel tidak dapat dibaca.") from exc

    # Hapus baris yang benar-benar kosong agar tidak ikut diproses.
    dataframe = dataframe.dropna(how="all")
    if dataframe.empty:
        raise DataLoadError("Dataset kosong.")

    # Pastikan semua kolom yang dibutuhkan aplikasi memang ada di file.
    missing_columns = [
        column
        for column in [ALTERNATIVE_COLUMN, *CRITERIA_METADATA.keys()]
        if column not in dataframe.columns
    ]
    if missing_columns:
        joined = ", ".join(missing_columns)
        raise DataLoadError(f"Kolom wajib tidak ditemukan: {joined}.")

    # Ambil hanya kolom yang relevan agar data lebih mudah diolah.
    working_frame = dataframe[[ALTERNATIVE_COLUMN, *CRITERIA_METADATA.keys()]].copy()
    working_frame = working_frame.dropna(subset=[ALTERNATIVE_COLUMN])
    if working_frame.empty:
        raise DataLoadError("Tidak ada alternatif yang valid di dalam dataset.")

    criteria = []
    for column_name, metadata in CRITERIA_METADATA.items():
        # Semua nilai kriteria harus bisa dibaca sebagai angka.
        numeric_series = pd.to_numeric(working_frame[column_name], errors="coerce")
        if numeric_series.isna().any():
            raise DataLoadError(
                f"Nilai pada kolom '{column_name}' harus seluruhnya numerik."
            )
        working_frame[column_name] = numeric_series.astype(float)
        criteria.append(
            {
                "label": column_name,
                "key": metadata["key"],
                "type": metadata["type"],
            }
        )

    alternatives = []
    for _, row in working_frame.iterrows():
        # Setiap baris Excel diubah menjadi satu alternatif dengan nilai per kriteria.
        values = {
            CRITERIA_METADATA[column]["key"]: float(row[column])
            for column in CRITERIA_METADATA
        }
        alternatives.append(
            {
                "name": str(row[ALTERNATIVE_COLUMN]),
                "values": values,
            }
        )

    return {
        "criteria": criteria,
        "alternatives": alternatives,
    }
