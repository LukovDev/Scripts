#
# vox_parser.py - Создаёт функцию для парсинга воксельного файла от MagicaVoxel а также приведены примеры использования.
#
# ! КОД ПРЕДНАЗНАЧЕН ДЛЯ ВЕРСИИ MagicaVoxel (0.99.7.1) !
#


# Получить данные из ".vox" файла:
def parse_vox_file(path: str, z_up_to_y_up: bool = True) -> dict:
    import struct

    # Структура получаемых данных:
    data = {
        "sizes":     [],  # Список размеров для каждой модели [X, Y, Z].
        "count":     [],  # Количество не пустых вокселей для каждой модели.
        "voxels":    [],  # Список всех не пустых вокселей для каждой модели [X, Y, Z, I].
        "palette":   [],  # Палитра цветов. Структура - (R, G, B, A).
        "materials": [],  # Список материалов (256 шт).
    }

    # Читаем файл:
    with open(path, "rb") as vox:
        # Утвердить что это VOX файл:
        assert (struct.unpack("<4c", vox.read(4)) == (b"V", b"O", b"X", b" "))

        # Считываем версию (не используется, но можно сохранить):
        version = struct.unpack("<i", vox.read(4))

        # Утвердить что это MAIN чанк:
        assert (struct.unpack("<4c", vox.read(4)) == (b"M", b"A", b"I", b"N"))
        N, M = struct.unpack("<ii", vox.read(8))
        assert (N == 0)

        # Проходимся по байтам:
        while True:
            try:
                *name, s_self, s_child = struct.unpack("<4cii", vox.read(12))
                name = b"".join(name).decode("utf-8")  # Декодирование названия чанка.

                # Проверка на наличие дочерних данных только для нужных чанков, если нужно
                if name in ["SIZE", "XYZI"]:  # Пример чанков, для которых может быть важен s_child
                    assert (s_child == 0)
            except struct.error: break  # Конец файла. Завершаем цикл.

            # Размер модели:
            if name == "SIZE":
                size = struct.unpack("<3i", vox.read(12))
                # Меняем Z и Y местами, потому что MagicaVoxel использует Z-Up координаты а не Y-Up как в OpenGL:
                if z_up_to_y_up: size = size[0], size[2], size[1]
                data["sizes"].append(size)

            # Воксели:
            elif name == "XYZI":
                num_voxels, = struct.unpack("<i", vox.read(4))
                model_voxels = []
                for voxel in range(num_voxels):
                    voxel_data = struct.unpack("<4B", vox.read(4))
                    # Вращаем и отражаем модель, так как MagicaVoxel использует Z-Up координаты а не Y-Up как в OpenGL:
                    if z_up_to_y_up: voxel_data = voxel_data[1], voxel_data[2], voxel_data[0], voxel_data[3]
                    model_voxels.append(voxel_data)
                data["voxels"].append(model_voxels)

            # Палитра:
            elif name == "RGBA":
                for col in range(256):
                    data["palette"].append(struct.unpack("<4B", vox.read(4)))

            # Материалы:
            elif name == "MATL":
                # Читаем ID материала и тип:
                matt_id, mat_type = struct.unpack("<ii", vox.read(8))

                # Оставшиеся данные - это свойства и их значения:
                mat_prps = {}

                # Оставшееся количество байт в чанке:
                remaining_bytes = s_self - 8
                while remaining_bytes > 0:
                    # Сначала читаем длину ключа (например, "_rough"):
                    key_len, = struct.unpack("<i", vox.read(4))
                    key = vox.read(key_len).decode("utf-8")
                    remaining_bytes -= 4 + key_len
                    
                    # Читаем длину значения:
                    value_len, = struct.unpack("<i", vox.read(4))
                    value = vox.read(value_len).decode("utf-8")
                    remaining_bytes -= 4 + value_len

                    # Добавляем свойство в словарь:
                    mat_prps[key] = value

                # Корректируем название материала:
                # Параметр cloud зашифрован под флагом _media, по этому делаем отдельную проверку для него.
                mat_names, mat_type = ["diffuse", "metal", "emit", "glass"], "diffuse"
                if "_type" in mat_prps:
                    mat_prps_type = mat_prps["_type"][1:]
                    if mat_prps_type in mat_names:
                        mat_type = mat_prps_type
                    elif mat_prps_type == "media":  # Проверяем на параметр cloud (под флагом media).
                        mat_type = "cloud"

                # Преобразуем параметры материала в нормальный вид (название материала и 10 параметров):
                material_properties = {
                    "type":  mat_type,                                                        # Тип материала.
                    "rough": 0.1 if "_rough" not in mat_prps else float(mat_prps["_rough"]),  # Roughness.
                    "ior":   0.3 if "_ior"   not in mat_prps else float(mat_prps["_ior"]  ),  # IOR.
                    "trans": 0.0 if "_trans" not in mat_prps else float(mat_prps["_trans"]),  # Transparent.
                    "dens":  0.0 if "_d"     not in mat_prps else float(mat_prps["_d"]    ),  # Density.
                    "phas":  0.0 if "_g"     not in mat_prps else float(mat_prps["_g"]    ),  # Phase.
                    "metal": 0.0 if "_metal" not in mat_prps else float(mat_prps["_metal"]),  # Metallic.
                    "spec":  0.0 if "_sp"    not in mat_prps else float(mat_prps["_sp"]   ),  # Specular.
                    "emit":  0.0 if "_emit"  not in mat_prps else float(mat_prps["_emit"] ),  # Emission.
                    "flux":  0.0 if "_flux"  not in mat_prps else float(mat_prps["_flux"] ),  # Power.
                    "ldr":   0.0 if "_ldr"   not in mat_prps else float(mat_prps["_ldr"]  ),  # Luminous Density Ratio.
                }

                # Сохраняем данные о материале:
                data["materials"].append(material_properties)

            # Игнорировать неизвестные чанки:
            else: vox.read(s_self)

    # Указываем количество непустых вокселей для каждой модели:
    data["count"] = [len(data["voxels"][i]) for i in range(len(data["voxels"]))]

    # Устанавливаем простой материал если материалов нет:
    if len(data["materials"]) == 0:
        data["materials"].append({
            "type":  "diffuse",
            "rough": 0.1,
            "ior":   0.3,
            "trans": 0.0,
            "dens":  0.0,
            "phas":  0.0,
            "metal": 0.0,
            "spec":  0.0,
            "emit":  0.0,
            "flux":  0.0,
            "ldr":   0.0,
        })

    # Устанавливаем палитру по умолчанию если палитр нет:
    if len(data["palette"]) == 0:
        data["palette"].append([
            0x00000000, 0xffffffff, 0xffccffff, 0xff99ffff, 0xff66ffff, 0xff33ffff, 0xff00ffff, 0xffffccff,
            0xffccccff, 0xff99ccff, 0xff66ccff, 0xff33ccff, 0xff00ccff, 0xffff99ff, 0xffcc99ff, 0xff9999ff,
            0xff6699ff, 0xff3399ff, 0xff0099ff, 0xffff66ff, 0xffcc66ff, 0xff9966ff, 0xff6666ff, 0xff3366ff,
            0xff0066ff, 0xffff33ff, 0xffcc33ff, 0xff9933ff, 0xff6633ff, 0xff3333ff, 0xff0033ff, 0xffff00ff,
            0xffcc00ff, 0xff9900ff, 0xff6600ff, 0xff3300ff, 0xff0000ff, 0xffffffcc, 0xffccffcc, 0xff99ffcc,
            0xff66ffcc, 0xff33ffcc, 0xff00ffcc, 0xffffcccc, 0xffcccccc, 0xff99cccc, 0xff66cccc, 0xff33cccc,
            0xff00cccc, 0xffff99cc, 0xffcc99cc, 0xff9999cc, 0xff6699cc, 0xff3399cc, 0xff0099cc, 0xffff66cc,
            0xffcc66cc, 0xff9966cc, 0xff6666cc, 0xff3366cc, 0xff0066cc, 0xffff33cc, 0xffcc33cc, 0xff9933cc,
            0xff6633cc, 0xff3333cc, 0xff0033cc, 0xffff00cc, 0xffcc00cc, 0xff9900cc, 0xff6600cc, 0xff3300cc,
            0xff0000cc, 0xffffff99, 0xffccff99, 0xff99ff99, 0xff66ff99, 0xff33ff99, 0xff00ff99, 0xffffcc99,
            0xffcccc99, 0xff99cc99, 0xff66cc99, 0xff33cc99, 0xff00cc99, 0xffff9999, 0xffcc9999, 0xff999999,
            0xff669999, 0xff339999, 0xff009999, 0xffff6699, 0xffcc6699, 0xff996699, 0xff666699, 0xff336699,
            0xff006699, 0xffff3399, 0xffcc3399, 0xff993399, 0xff663399, 0xff333399, 0xff003399, 0xffff0099,
            0xffcc0099, 0xff990099, 0xff660099, 0xff330099, 0xff000099, 0xffffff66, 0xffccff66, 0xff99ff66,
            0xff66ff66, 0xff33ff66, 0xff00ff66, 0xffffcc66, 0xffcccc66, 0xff99cc66, 0xff66cc66, 0xff33cc66,
            0xff00cc66, 0xffff9966, 0xffcc9966, 0xff999966, 0xff669966, 0xff339966, 0xff009966, 0xffff6666,
            0xffcc6666, 0xff996666, 0xff666666, 0xff336666, 0xff006666, 0xffff3366, 0xffcc3366, 0xff993366,
            0xff663366, 0xff333366, 0xff003366, 0xffff0066, 0xffcc0066, 0xff990066, 0xff660066, 0xff330066,
            0xff000066, 0xffffff33, 0xffccff33, 0xff99ff33, 0xff66ff33, 0xff33ff33, 0xff00ff33, 0xffffcc33,
            0xffcccc33, 0xff99cc33, 0xff66cc33, 0xff33cc33, 0xff00cc33, 0xffff9933, 0xffcc9933, 0xff999933,
            0xff669933, 0xff339933, 0xff009933, 0xffff6633, 0xffcc6633, 0xff996633, 0xff666633, 0xff336633,
            0xff006633, 0xffff3333, 0xffcc3333, 0xff993333, 0xff663333, 0xff333333, 0xff003333, 0xffff0033,
            0xffcc0033, 0xff990033, 0xff660033, 0xff330033, 0xff000033, 0xffffff00, 0xffccff00, 0xff99ff00,
            0xff66ff00, 0xff33ff00, 0xff00ff00, 0xffffcc00, 0xffcccc00, 0xff99cc00, 0xff66cc00, 0xff33cc00,
            0xff00cc00, 0xffff9900, 0xffcc9900, 0xff999900, 0xff669900, 0xff339900, 0xff009900, 0xffff6600,
            0xffcc6600, 0xff996600, 0xff666600, 0xff336600, 0xff006600, 0xffff3300, 0xffcc3300, 0xff993300,
            0xff663300, 0xff333300, 0xff003300, 0xffff0000, 0xffcc0000, 0xff990000, 0xff660000, 0xff330000,
            0xff0000ee, 0xff0000dd, 0xff0000bb, 0xff0000aa, 0xff000088, 0xff000077, 0xff000055, 0xff000044,
            0xff000022, 0xff000011, 0xff00ee00, 0xff00dd00, 0xff00bb00, 0xff00aa00, 0xff008800, 0xff007700,
            0xff005500, 0xff004400, 0xff002200, 0xff001100, 0xffee0000, 0xffdd0000, 0xffbb0000, 0xffaa0000,
            0xff880000, 0xff770000, 0xff550000, 0xff440000, 0xff220000, 0xff110000, 0xffeeeeee, 0xffdddddd,
            0xffbbbbbb, 0xffaaaaaa, 0xff888888, 0xff777777, 0xff555555, 0xff444444, 0xff222222, 0xff111111
        ])

    return [{
        "size": data["sizes"][i],
        "count": data["count"][i],
        "voxels": data["voxels"][i],
        "palette": data["palette"],
        "material": data["materials"][i],
    } for i in range(len(data["sizes"]))]


# Тестируем функцию загружая файл:
import time
t = time.time()
# В функции есть параметр z_up_to_y_up. Если его поставить в True, то модель будет пересена в систему координат OpenGL.
# Но эта конвертация замедлит функцию в ~1.37 раз. Не критично, но имейте в виду.
voxel_data = parse_vox_file("voxel.vox")
print(f"Parsed in: {time.time()-t}\n")

# Выберем одну модель:
voxel_model = voxel_data[0]

# Размер модели в формате [X, Y, Z]:
print(f"Size: {voxel_model['size']}\n")

# Количество не пустых вокселей в модели:
print(f"Count: {voxel_model['count']}\n")

# Список вокселей. Модель в виде списка значений вокселя.
# Воксель представляет из себя [X, Y, Z, I] структуру, где I это индекс от 0 до 255 в списке материалов и палитры цвета:
print(f"Voxels: {voxel_model['voxels']}\n")

# Палитра (256 цветов):
print(f"Palette: {voxel_model['palette']}\n")

# Материалы (256 штук):
""" Примерно так выглядит структура материала (это словарь):
    {
        'type': 'diffuse',
        'rough': 0.1,
        'ior': 0.3,
        'trans': 0.0,
        'dens': 0.05,
        'phas': 0.0,
        'metal': 0.0,
        'spec': 0.0,
        'emit': 0.0,
        'flux': 0.0,
        'ldr': 0.0
    }
"""

# Получаем цвет вокселя:
# ["voxels"][номер вокселя в списке][последний элемент обозначающий индекс материала и палитры]:
vox_mat_id = voxel_model["voxels"][0][-1]  # Тут мы получили id палитры и материала вокселя.

# Получили цвет вокселя:
color = voxel_model["palette"]  # R, G, B, A.

# Получили материал вокселя:
material = voxel_model["material"]  # Dict type.

# Выводим полученный цвет и материал:
print(f"Color: {color}\n")
print(f"Material: {material}")


# Можно конечно получить воксель и по его координатам, но тут уже надо превратить список вокселей в словарь.
# Чтобы структура словаря была типа такой: {(x, y, z): m_id}
""" Это можно сделать так:
    
    # Предварительно создаём словарь вокселей. (Можете вынести в отдельную функцию):
    voxels = voxel_model["voxels"]
    voxel_dict = {}
    for voxel in voxels:
        x, y, z, m_id = voxel
        voxel_dict[(x, y, z)] = m_id

        # или:
        # voxel_dict[*voxel[:3]] = voxel[3]

    # Получаем воксель из координат:
    voxel_dict.get((x, y, z))
"""
