def analyze_routine(routine):
    recommendations = []

    if routine.wake_time and routine.wake_time.hour >= 9:
        recommendations.append(
            "Uyg‘onish vaqti kech. Ertalabki intellektual samaradorlik pasaymoqda."
        )

    if routine.night_work_end and routine.night_work_end.hour >= 1:
        recommendations.append(
            "Kechasi 01:00 dan keyin ishlash — stressni oshiradi va keyingi kun energiyani pasaytiradi."
        )

    if routine.energy_level == "low":
        recommendations.append(
            "Bugun energiya past. Murakkab ishlarni ertaga ko‘chirish tavsiya etiladi."
        )

    if routine.sleep_quality == "low":
        recommendations.append(
            "Uyqu sifati past. Bugun og‘ir qarorlar qabul qilmaslik tavsiya etiladi."
        )

    if not recommendations:
        recommendations.append("Kun tartibingiz optimal holatda.")

    return recommendations
