def calculate_wsm(dataset: dict, raw_weights: dict[str, float]) -> dict:
    """Menghitung seluruh proses WSM sampai menghasilkan ranking akhir.

    Fungsi ini menerima data alternatif dan bobot mentah, lalu menjalankan empat
    tahap utama: normalisasi bobot, mencari nilai minimum/maksimum tiap kriteria,
    menghitung kontribusi setiap alternatif, dan menyusun ranking dari skor terbesar.
    """
    criteria = dataset["criteria"]
    alternatives = dataset["alternatives"]

    weights = _normalize_weights(criteria, raw_weights)
    normalized_matrix = []
    contribution_matrix = []
    ranking = []

    # Simpan nilai minimum dan maksimum setiap kriteria untuk rumus normalisasi.
    extrema = {}
    for criterion in criteria:
        key = criterion["key"]
        values = [alternative["values"][key] for alternative in alternatives]
        extrema[key] = {"min": min(values), "max": max(values)}

    for alternative in alternatives:
        # Satu alternatif diproses untuk menghitung nilai normalisasi dan skor totalnya.
        normalized_row = {"name": alternative["name"], "values": {}}
        contribution_row = {"name": alternative["name"], "values": {}}
        score = 0.0

        for criterion in criteria:
            key = criterion["key"]
            value = alternative["values"][key]
            normalized_value = _normalize_value(value, criterion["type"], extrema[key])
            contribution = normalized_value * weights[key]

            # Kontribusi adalah nilai normalisasi yang sudah dikalikan bobot.
            normalized_row["values"][key] = normalized_value
            contribution_row["values"][key] = contribution
            score += contribution

        normalized_matrix.append(normalized_row)
        contribution_matrix.append(contribution_row)
        ranking.append(
            {
                "name": alternative["name"],
                "score": score,
                "raw_values": alternative["values"],
            }
        )

    ranking.sort(key=lambda item: item["score"], reverse=True)
    # Setelah diurutkan, tiap alternatif diberi nomor peringkat mulai dari 1.
    for index, item in enumerate(ranking, start=1):
        item["rank"] = index

    return {
        "criteria": criteria,
        "alternatives": alternatives,
        "weights": weights,
        "ranking": ranking,
        "normalized_matrix": normalized_matrix,
        "contribution_matrix": contribution_matrix,
    }


def _normalize_weights(criteria: list[dict], raw_weights: dict[str, float]) -> dict[str, float]:
    """Mengubah bobot mentah menjadi bobot proporsional dengan total 1.

    Tujuannya agar semua kriteria tetap seimbang. Misalnya jika total bobot dari
    form adalah 200, setiap nilai akan dibagi 200 sehingga total akhir menjadi 1.
    """
    selected_weights = {
        criterion["key"]: float(raw_weights[criterion["key"]]) for criterion in criteria
    }
    total = sum(selected_weights.values())
    if total <= 0:
        raise ValueError("Total bobot harus lebih besar dari 0.")
    return {key: value / total for key, value in selected_weights.items()}


def _normalize_value(value: float, criterion_type: str, extrema: dict[str, float]) -> float:
    """Menormalisasi satu nilai kriteria sesuai jenisnya: benefit atau cost.

    Untuk benefit, nilai yang lebih besar dianggap lebih baik sehingga dibagi nilai
    maksimum. Untuk cost, nilai yang lebih kecil dianggap lebih baik sehingga nilai
    minimum dibagi nilai saat ini.
    """
    if criterion_type == "benefit":
        denominator = extrema["max"]
        return 0.0 if denominator == 0 else value / denominator

    denominator = value
    numerator = extrema["min"]
    return 0.0 if denominator == 0 else numerator / denominator
