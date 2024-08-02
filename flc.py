#
# flc.py - Посчитать количество строк во всех файлах в каталоге и подкаталогах.
#

import os

def count_lines_in_directory(directory: str, self_name: str, format: str) -> int:
    format = [format] if not isinstance(format, list) else format
    total_lines = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.isfile(file_path) and file != self_name and os.path.splitext(file)[1] in format:
                with open(file_path, "r+", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()
                    total_lines += len(lines)
                    print(f"{file} -> {len(lines)} lines")

    return total_lines

# Считаем:
total_lines = count_lines_in_directory(
    "./",            # Путь до папки где надо посчитать.
    "flc.py",        # Название этого файла (чтобы не посчитать строки в этом файле).
    [".py", ".pyx"]  # Список расширений форматов файлов.
)

print(f"\nTotal lines in all files: {total_lines}")
