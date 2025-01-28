#
# perlin.py - Создаёт разные реализации шума перлина на питоне.
#


# Импортируем:
import math


# Простой бесконечный генератор шума перлина из двух координат и сида:
def simple_perlin_noise(x: float, y: float, stretch: float, seed: int) -> float:
    """
    Параметры:
        x, y: Координаты.
        stretch: Масштабирование шума (например, уменьшение или увеличение частоты).
        seed: Ключ генерации шума.
    """

    # Шум Перлина:
    def get_noise(x: float, y: float, seed: int) -> float:
        if seed > 0:
            x -= seed
            y -= seed
        n = x + y * 57
        n = (n << 13) ^ n
        return 1.0 - ((n * (n * n * 15731 + 789221) + 1376312589) & 0x7fffffff) / 1073741824.0

    # Растянуть шум Перлина:
    def stretched_noise(xf: float, yf: float, stretch: float, seed: int) -> float:
        # Растянуть шум:
        xf /= stretch
        yf /= stretch

        # Целая часть координат:
        x, y = math.floor(xf), math.floor(yf)
        fractional_X = xf - x

        # Нам нужно захватить ближайшие точки 4x4, чтобы выполнить кубическую интерполяцию:
        def cubic_interp(p, x):
            P = (p[3] - p[2]) - (p[0] - p[1])
            Q = (p[0] - p[1]) - P
            R = p[2] - p[0]
            return P * x ** 3 + Q * x ** 2 + R * x + p[1]

        # Интерполяция на заданной точке:
        p = []
        for j in range(4):
            p2 = [get_noise(x + i - 1, y + j - 1, seed) for i in range(4)]
            p.append(cubic_interp(p2, fractional_X))  # Интерполируйте каждую строку.

        return cubic_interp(p, yf - y)  # Интерполируйте результаты интерполяции каждой строки.
    return stretched_noise(x, y, stretch, seed)


# Расширенная функция шума Перлина с параметрами масштабирования и наклона:
def perlin_noise_2(x: float, y: float, stretch: float, tilt: float, octaves: int = 1, persistence: float = 0.5, lacunarity: float = 2.0, seed: int = 0) -> float:
    """
    Параметры:
        x, y: Координаты.
        stretch: Масштабирование шума (например, уменьшение или увеличение частоты).
        tilt: Наклон шума, значение от -1 до 1 (для поворота на 45 градусов, но можно и больше).
        octaves: Количество октав (слоёв шума).
        persistence: Влияние каждой октавы (амплитуда).
        lacunarity: Масштабирование каждой последующей октавы.
        seed: Ключ генерации шума.
    """

    # Шум Перлина:
    def get_noise(x: float, y: float, seed: int) -> float:
        if seed > 0:
            x -= seed
            y -= seed
        n = x + y * 57
        n = (n << 13) ^ n
        return 1.0 - ((n * (n * n * 15731 + 789221) + 1376312589) & 0x7fffffff) / 1073741824.0

    # Растянуть шум Перлина:
    def stretched_noise(xf: float, yf: float, scale: float, tilt: float, seed: int) -> float:
        # Нам нужно захватить ближайшие точки 4x4, чтобы выполнить кубическую интерполяцию:
        def cubic_interp(p, x):
            P = (p[3] - p[2]) - (p[0] - p[1])
            Q = (p[0] - p[1]) - P
            R = p[2] - p[0]
            return P * x ** 3 + Q * x ** 2 + R * x + p[1]

        # Растянуть шум:
        xf /= stretch
        yf /= stretch

        # Применяем наклон:
        if tilt != 0: xf += tilt * yf

        # Целая часть координат:
        x, y = math.floor(xf), math.floor(yf)
        fractional_X = xf - x
        fractional_Y = yf - y

        # Генерация сетки 4x4 для интерполяции:
        p = []
        for j in range(4):
            p2 = [get_noise(x + i - 1, y + j - 1, seed) for i in range(4)]
            p.append(cubic_interp(p2, fractional_X))

        return cubic_interp(p, fractional_Y)

    # Многослойный шум (октавы):
    total = 0
    max_value = 0
    amplitude = 1.0
    frequency = 1.0

    for _ in range(octaves):
        total += stretched_noise(x * frequency, y * frequency, stretch, tilt, seed) * amplitude
        max_value += amplitude
        amplitude *= persistence
        frequency *= lacunarity

    return total / max_value
  
