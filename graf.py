import matplotlib.pyplot as plt
from io import BytesIO

def build_smoking_stats(history):
    if not history:
        return None

    dates = [h[0] for h in history]       # даты
    cigs = [h[1] for h in history]        # сигареты
    vapes = [h[2] for h in history]       # вейп

    plt.figure(figsize=(8, 5))
    plt.plot(dates, cigs, marker="o", label="Сигареты")
    plt.plot(dates, vapes, marker="s", label="Вейп")
    plt.title("Статистика курения за период")
    plt.xlabel("Дата")
    plt.ylabel("Количество")
    plt.xticks(rotation=45, ha="right")
    plt.legend()
    plt.tight_layout()
    plt.grid(True)

    buf = BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close()

    return buf