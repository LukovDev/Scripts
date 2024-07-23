#
# cliker.py - Автокликер, созданный LukovDev.
#


# Импортируем:
if True:
    import time
    import mouse
    import keyboard


# Параметры:
button = 0        # 0 = LEFT | 1 = MIDDLE | 2 = RIGHT.
cps    = 100      # Кликов в секунду.
hotkey = "num -"  # Горячая клавиша на клавиатуре.
exit_k = "num *"  # Выход из автокликера.


# Внутренние переменные:
is_ext = False  # Выйти ли из автокликера.
work   = False  # Включен ли автокликер.

# Делаем бинды на клавиши клавиатуры:
keyboard.add_hotkey(hotkey.lower(), lambda: globals().update(work=not globals()["work"]))      # Бинд на активацию.
keyboard.add_hotkey(exit_k.lower(), lambda: globals().update(is_ext=not globals()["is_ext"]))  # Бинд на выход.


# Бесконечно быстро обрабатываем клики:
while not is_ext:
    if work:
        mouse.click(button=["left", "middle", "right"][button])
    time.sleep(1/cps)
