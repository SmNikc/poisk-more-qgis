import os
from datetime import datetime


def generate_log_summary(input_path: str = "operator_log.txt", output_path: str = "log_summary.txt") -> None:
    """Generate a short summary from the operator log file."""
    if not os.path.exists(input_path):
        print("Входной файл не найден.")
        return

    try:
        with open(input_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        summary: dict[datetime.date, int] = {}
        for line in lines:
            if "[" in line and "]" in line:
                date_str = line.split("]")[0].strip("[]").split(" ")[0]
                try:
                    date = datetime.strptime(date_str, "%Y-%m-%d").date()
                    summary[date] = summary.get(date, 0) + 1
                except ValueError:
                    continue

        with open(output_path, "w", encoding="utf-8") as f:
            for date, count in sorted(summary.items()):
                f.write(f"{date}: {count} action(s)\n")
    except Exception as e:
        print(f"Ошибка генерации сводки: {e}")
