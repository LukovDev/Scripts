#
# image_to_rgba_array.py - Преобразует картинку в C-массив.
#


# Импортируем:
import sys
from PIL import Image


# Конвертируем картинку в C-массив:
def convert(image_path, output_path, var_name="embedded_icon") -> None:
    img = Image.open(image_path).convert("RGBA")
    data = img.tobytes()
    width, height = img.size

    # Форматируем: каждые 16 байт = новая строка:
    lines = []
    for i in range(0, len(data), 16):
        chunk = data[i:i+16]
        line = ", ".join(f"0x{b:02X}" for b in chunk)
        lines.append("    " + line + ",")
    array_str = "\n".join(lines)

    c_code = f"""//
// {output_path} - Встроенное RGBA изображение ({width}x{height}).
// Сгенерировано: By LukovDev 2025.
//


// Подключаем:
#include <stddef.h>
#include <stdint.h>


// Набор байтов картинки:
const unsigned char {var_name}[] = {{
{array_str}
}};

const size_t {var_name}_size = sizeof({var_name});  // Размер картинки в байтах.
const int {var_name}_width  = {width};  // Ширина картинки.
const int {var_name}_height = {height};  // Высота картинки.
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(c_code)

    print(f"\n[OK] {image_path} → {output_path} (RGBA {width}x{height}, {len(data)} bytes)")


# Если этот скрипт запускают:
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("\nUsing: python3 image_to_carray.py input.png output.c [var_name]\n")
        sys.exit(1)

    image_path = sys.argv[1]
    output_path = sys.argv[2]
    var_name = sys.argv[3] if len(sys.argv) > 3 else "embedded_icon"

    convert(image_path, output_path, var_name)
