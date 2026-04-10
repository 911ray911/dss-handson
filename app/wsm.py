
def calculate_wsm(dataset: dict, raw_weights: dict[str, float]) -> dict:
    """Menghitung seluruh proses WSM sampai menghasilkan ranking akhir.

    Fungsi ini menerima data alternatif dan bobot mentah, lalu menjalankan empat
    tahap utama: normalisasi bobot, mencari nilai minimum/maksimum tiap kriteria,
    menghitung kontribusi setiap alternatif, dan menyusun ranking dari skor terbesar.
    """
    criteria_list = dataset["criteria"]
    alternative_list = dataset["alternatives"]

    normalized_weights = _normalize_weights(criteria_list, raw_weights)
    normalized_matrix = []
    contribution_matrix = []
    ranking = []

    # Simpan nilai minimum dan maksimum setiap kriteria untuk rumus normalisasi.
    criterion_extrema = {}
    for criterion in criteria_list:
        criterion_key = criterion["key"]
        criterion_values = [
            alternative["values"][criterion_key] for alternative in alternative_list
        ]
        criterion_extrema[criterion_key] = {
            "min": min(criterion_values),
            "max": max(criterion_values),
        }

    for alternative in alternative_list:
        # Satu alternatif diproses untuk menghitung nilai normalisasi dan skor totalnya.
        normalized_row = {"name": alternative["name"], "values": {}}
        contribution_row = {"name": alternative["name"], "values": {}}
        total_score = 0.0

        for criterion in criteria_list:
            criterion_key = criterion["key"]
            criterion_value = alternative["values"][criterion_key]
            normalized_value = _normalize_value(
                criterion_value,
                criterion["type"],
                criterion_extrema[criterion_key],
            )
            # TUGAS: Hitung kontribusi berbobot untuk kriteria ini.
            # Rumus: nilai_yang_sudah_dinormalisasi * bobot_kriteria_ini
            # Petunjuk: hasil normalisasi sudah tersimpan di variabel normalized_value
            weighted_contribution = XXX * normalized_weights[criterion_key]  # ganti XXX

            # Kontribusi adalah nilai normalisasi yang sudah dikalikan bobot.
            normalized_row["values"][criterion_key] = normalized_value
            contribution_row["values"][criterion_key] = weighted_contribution
            total_score += weighted_contribution

        normalized_matrix.append(normalized_row)
        contribution_matrix.append(contribution_row)
        ranking.append(
            {
                "name": alternative["name"],
                "score": total_score,
                "raw_values": alternative["values"],
            }
        )

    ranking.sort(key=lambda item: item["score"], reverse=True)
    # Setelah diurutkan, tiap alternatif diberi nomor peringkat mulai dari 1.
    for index, item in enumerate(ranking, start=1):
        item["rank"] = index

    return {
        "criteria": criteria_list,
        "alternatives": alternative_list,
        "weights": normalized_weights,
        "ranking": ranking,
        "normalized_matrix": normalized_matrix,
        "contribution_matrix": contribution_matrix,
    }


def _normalize_weights(criteria: list[dict], raw_weights: dict[str, float]) -> dict[str, float]:
    """Mengubah bobot mentah menjadi bobot proporsional dengan total 1.

    Tujuannya agar semua kriteria tetap seimbang. Misalnya jika total bobot dari
    form adalah 200, setiap nilai akan dibagi 200 sehingga total akhir menjadi 1.
    """
    active_weights = {
        criterion["key"]: float(raw_weights[criterion["key"]]) for criterion in criteria
    }
    total_weight = sum(active_weights.values())
    if total_weight <= 0:
        raise ValueError("Total bobot harus lebih besar dari 0.")
    return {key: value / total_weight for key, value in active_weights.items()}


def _normalize_value(value: float, criterion_type: str, extrema: dict[str, float]) -> float:
    """Menormalisasi satu nilai kriteria sesuai jenisnya: benefit atau cost.

    Untuk benefit, nilai yang lebih besar dianggap lebih baik sehingga dibagi nilai
    maksimum. Untuk cost, nilai yang lebih kecil dianggap lebih baik sehingga nilai
    minimum dibagi nilai saat ini.
    """
    if criterion_type == "benefit":
        # TUGAS: Untuk benefit, nilai yang lebih BESAR lebih baik.
        # Rumus: nilai_saat_ini / nilai_TERBESAR dari semua alternatif
        # Petunjuk: nilai terbesar tersimpan di extrema["max"]
        denominator = extrema["max"]
        return 0.0 if denominator == 0 else XXX / denominator  # ganti XXX dengan variabel yang tepat

    # TUGAS: Untuk cost, nilai yang lebih KECIL lebih baik.
    # Rumus: nilai_TERKECIL dari semua alternatif / nilai_saat_ini
    # Petunjuk: nilai terkecil tersimpan di extrema["min"], nilai saat ini ada di parameter value
    denominator = XXX   # ganti XXX: nilai saat ini yang dijadikan pembagi
    numerator = XXX     # ganti XXX: nilai terkecil dari semua alternatif
    return 0.0 if denominator == 0 else numerator / denominator
