from __future__ import annotations

import random
from typing import Final

GREETING_PHRASES: Final[list[str]] = [
    "На пороге таверны появляется новое лицо. Смотритель бросает взгляд из-подо лба, оценивает посетителя и молча откладывает перо.",
    "Дверь скрипит. В зал входит незнакомец. Смотритель поднимает голову от записей — и снова опускает.",
    "Порог переступает ещё один странник. Смотритель прикрывает книгу и чуть заметно кивает. Таверна видела всяких.",
    "В зал входит новый гость. Смотритель откидывается на спинку стула и смотрит долго, не торопясь.",
    "Чья-то тень мелькает у входа. На миг в зале становится тише. Смотритель поднимает взгляд — и молчит.",
]


def pick_phrase(last_index: int) -> tuple[str, int]:
    available = [i for i in range(len(GREETING_PHRASES)) if i != last_index]
    index = random.choice(available)
    return GREETING_PHRASES[index], index
