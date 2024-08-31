#
# filter.py - Создаёт класс фильтрации сообщений.
#


# Импортируем:
import re


# Класс фильтра:
class TextFilter:
    # Фильтрация текста:
    @staticmethod
    def filter_text(full_text: str, words: list[str], replace_word: str) -> str:
        """ Принимает исходный текст, список слов для замены и слово на которое будет заменены слова из списка. """

        # Возвращаем отфильтрованный текст:
        return re.sub(
            "|".join(r"\b" + r"\s*".join(re.escape(char) for char in word) + r"\b" for word in words),
            replace_word,
            full_text,
            flags=re.IGNORECASE
        )
