#
# vox_parser.py - Создаёт функцию для парсинга воксельного файла от MagicaVoxel а также приведены примеры использования.
#
# ! КОД ПРЕДНАЗНАЧЕН ДЛЯ ВЕРСИИ MagicaVoxel (0.99.7.1) !
#


# Получить данные из ".vox" файла:
def load_vox_file(path: str, z_up_to_y_up: bool = True) -> dict:
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
                    # Меняем Z и Y местами, потому что MagicaVoxel использует Z-Up координаты а не Y-Up как в OpenGL:
                    if z_up_to_y_up: voxel_data = voxel_data[0], voxel_data[2], voxel_data[1], voxel_data[3]
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

                # Преобразуем параметры материала в нормальный вид (тип материала и 10 параметров):
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

    return data


# Тестируем функцию загружая файл:
import time
t = time.time()
# В функции есть параметр z_up_to_y_up. Если его поставить в True, то модель будет пересена в систему координат OpenGL.
# Но эта конвертация замедлит функцию в ~1.37 раз. Не критично, но имейте в виду.
voxel_data = load_vox_file("test.vox")
print(f"Parsed in: {time.time()-t}\n")

# Размеры всех моделей в формате [X, Y, Z]:
print(f"Sizes: {voxel_data['sizes']}\n")

# Количество не пустых вокселей в каждой модели:
print(f"Count: {voxel_data['count']}\n")

# Список списков вокселей. Каждый элемент списка - модель в виде списка значений вокселя.
# Воксель представляет из себя [X, Y, Z, I] структуру, где I это индекс от 0 до 255 в списке материалов и палитры цвета:
print(f"Voxels: {voxel_data['voxels']}\n")

# Палитра (256 цветов):
print(f"Palette: {voxel_data['palette']}\n")

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
print(f"Materials: {voxel_data['materials']}\n")


# Получаем цвет вокселя:
# ["voxels"][id модели][номер вокселя в списке][последний элемент обозначающий индекс материала и палитры]:
vox_mat_id = voxel_data["voxels"][0][0][-1]  # Тут мы получили id палитры и материала вокселя.

# Получили цвет вокселя:
color = voxel_data["palette"][vox_mat_id]  # R, G, B, A.

# Получили материал вокселя:
material = voxel_data["materials"][vox_mat_id]  # Dict type.

# Выводим полученный цвет и материал:
print(f"Color: {color}\n")
print(f"Material: {material}")


# Можно конечно получить воксель и по его координатам, но тут уже надо превратить список вокселей в словарь.
# Чтобы структура словаря была типа такой: {(x, y, z): m_id}
""" Это можно сделать так:
    
    # Предварительно создаём словарь вокселей. (Можете вынести в отдельную функцию):
    voxels = voxel_data["voxels"][<Номер модели. Например: 0>]
    voxel_dict = {}
    for voxel in voxels:
        x, y, z, m_id = voxel
        voxel_dict[(x, y, z)] = m_id

        # или:
        # voxel_dict[*voxel[:3]] = voxel[3]

    # Получаем воксель из координат:
    voxel_dict.get((x, y, z))
"""
