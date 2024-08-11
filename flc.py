#
# flc.py - Посчитать количество строк во всех файлах в папке.
#

import os
import sys

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
root_directory    = "./"             # Путь до папки где надо посчитать.
name_of_this_file = "flc.py"         # Название этого файла.
file_format       = [".py", ".pyx"]  # Форматы файлов.
if len(sys.argv) > 1: total_lines = count_lines_in_directory(sys.argv[1], name_of_this_file, sys.argv[2:])
else: total_lines = count_lines_in_directory(root_directory, name_of_this_file, file_format)

print(f"\nTotal lines in all files: {total_lines}")
