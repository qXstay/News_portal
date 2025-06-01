from django import template
import re

register = template.Library()

# Список запрещённых слов. Например, "редиска".
BANNED_WORDS = ['редиска']


@register.filter(name='censor')
def censor(value):
    if not isinstance(value, str):
        raise ValueError("Фильтр censor применяется только к строковым переменным")

    def repl(match):
        word = match.group()
        return word[0] + '*' * (len(word) - 1)

    # Для каждого запрещённого слова создаём паттерн, учитывающий вариант с первой буквой в верхнем и в нижнем регистре.
    for banned in BANNED_WORDS:
        pattern = r'\b(?:' + re.escape(banned) + '|' + re.escape(banned.capitalize()) + r')\b'
        value = re.sub(pattern, repl, value)
    return value