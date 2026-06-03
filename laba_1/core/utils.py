import re

def parse_time_to_seconds(time_str: str) -> float | None:
    if not time_str:
        return None
    s = time_str.replace(":", ".").replace(",", ".")
    try:
        if re.fullmatch(r'\d+\.\d{2}', s):
            return float(s)
        elif len(s.split(".")) == 3:  # 3.31.25
            m, sec, cent = map(int, s.split("."))
            return m * 60 + sec + cent / 100
        elif ":" in time_str:
            parts = time_str.replace(",", ".").split(":")
            mins = int(parts[0])
            rest = float(parts[1])
            return mins * 60 + rest
        else:
            return float(s)
    except:
        return None

def format_time(seconds: float) -> str:
    """Преобразует секунды в формат MM:SS,cc"""
    mins = int(seconds // 60)
    secs = seconds % 60
    return f"{mins:02}:{secs:05.2f}".replace(".", ",")

def get_points_by_place(place: int) -> int:
    points = [50, 46, 42, 39, 36, 33, 30, 27, 24, 22, 20, 18, 16, 14, 12, 10, 8, 7, 6, 5, 4, 3, 2, 1]
    if 1 <= place <= 24:
        return points[place - 1]
    else:
        return 1  # Все места после 24 — по 1 очку

def normalize_event_name(title: str) -> str:
    """Главная функция нормализации."""
    # 1. Очистка от мусора
    clean_title = clean_raw_text(title)

    # 2. Извлечение компонентов
    sport = normalize_sport_type(clean_title)
    distance = normalize_distance(clean_title)
    category = normalize_category(clean_title)

    # 3. Сборка итоговой строки
    # Формат: Вид спорта - Дистанция Категория
    return f"{sport} - {distance} {category}"

def is_event_header(line):
        """Определяет заголовок дисциплины."""
        line_lower = line.lower()
        document_headers = [
        'всероссийские соревнования',
        'группы спортивных дисциплин',
        'снежные ласты',
        'первенство россии',
        'кубок россии',
        'чемпионат россии'
    ]
        if any(header in line_lower for header in document_headers):
            return False

        # Ищем строки, содержащие тип дистанции и возрастную категорию
        keywords = ['плавание', 'ныряние', 'подводное', 'классическ', 'ласт',]
        age_groups = ['юниоры', 'юниорки', 'юноши', 'девушки', 'мужчины', 'женщины', 'мальчики', 'девочки']

        has_keyword = any(k in line_lower for k in keywords)
        has_age = any(ag in line_lower for ag in age_groups)

        distances = ['50', '100', '200', '400', '800', '1500', '4х50', '4х100', '4х200']
        has_distance = any(d in line_lower for d in distances)

        return has_keyword and has_age and (has_distance or 'эстафета' in line_lower)

def is_athlete_row(parts):
        NON_ATHLETE_KEYWORDS = [
    'протокол', 'технических', 'результатов', 'место', 'разряд',
    'фамилия', 'имя', 'год', 'рожд', 'команда', 'результат',
    'норматив', 'очки', 'предв', 'финал', 'главный', 'судья',
    'секретарь', 'соревнований', 'федерация', 'министерство',
    'первенство', 'чемпионат', 'соревнования', 'протокол',
    'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля',
    'августа', 'сентября', 'октября', 'ноября', 'декабря',
    'января', 'дистанция', 'дисциплина', 'день', 'переныр', '15м',
    'медотвод', 'отвод', 'н/я', 'ф/с', 'н/кас повор', 'касание'

]
        if not parts:
            return False

        # Объединяем первые несколько частей для проверки
        text_check_start = ' '.join(parts[:min(5, len(parts))]).lower()
        # Объединяем последние несколько частей для проверки
        text_check_end = ' '.join(parts[-5:]).lower()


        # Проверка на наличие ключевых слов не-спортсмена
        for keyword in NON_ATHLETE_KEYWORDS:
            if keyword in text_check_start or keyword in text_check_end:
                return False

        # Проверка на дату в формате "26 февраля-01 марта 2025 г."
        date_pattern = r'\d{1,2}\s*(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)'
        import re
        if re.search(date_pattern, text_check_start, re.IGNORECASE):
            return False

        return True

def normalize_line(line):
            # 1. Добавляем пробелы между временем и разрядом: "59,03III" -> "59,03 III"
            line = re.sub(r'(\d{1,2}[,.:]\d{2}(?:[,.:]\d{2})?)([IКМСб\\/юн])', r'\1 \2', line)

            # 2. Добавляем пробелы между разрядом и "юн": "IIIюн" -> "III юн"
            line = re.sub(r'([I]{1,3}|[1-3])(юн)', r'\1 \2', line)

            # 3. Обрабатываем сложные случаи: "59,03IIIюн" -> "59,03 III юн"
            line = re.sub(r'(\d{1,2}[,.:]\d{2}(?:[,.:]\d{2})?)([I]{1,3}|[1-3])(юн)', r'\1 \2 \3', line)
            return line

def get_best_time(*results):
    valid_pairs = []
    for r in results:
        if r is None:
            continue
        sec = parse_time_to_seconds(r)
        if sec is not None:
            valid_pairs.append((sec, r))

    if not valid_pairs:
        return None

    # Находим минимальное по секундам и возвращаем исходную строку
    best_sec, best_str = valid_pairs[0]
    for sec, s in valid_pairs[1:]:
        if sec < best_sec:
            best_sec = sec
            best_str = s
    return best_str


def clean_raw_text(text: str) -> str:
    """Удаляет коды дисциплин, лишние пробелы и знаки препинания."""
    # Удаляем всё в скобках (коды дисциплин)
    text = re.sub(r'\([^)]*\)', '', text)
    # Удаляем лишние пробелы
    text = re.sub(r'\s+', ' ', text).strip()
    # Убираем точки в конце, если есть
    text = text.rstrip('.')
    return text

def normalize_sport_type(title: str) -> str:
    """Определяет и нормализует название вида спорта."""
    title_lower = title.lower()

    if "ныряние" in title_lower:
        return "Подводное плавание"
    elif "классическ" in title_lower:
        return "Плавание в классических ластах"
    elif "подводное" in title_lower:
        return "Подводное плавание"
    elif "плавание" in title_lower and "ласт" in title_lower:
        return "Плавание в ластах"
    elif "плавание" in title_lower:
        # Если просто плавание без упоминания ласт, но в контексте подводного спорта
        return "Плавание в ластах"
    else:
        return "Дисциплина"

def normalize_category(title: str) -> str:
    """ Приводит 6 возрастных категорий к единому стандарту."""
    title_lower = title.lower()

    # Женские категории
    if "юниорк" in title_lower: # юниорки
        return "Женщины"
    if "девуш" in title_lower or "девоч" in title_lower: # девушки, девочки
        return "Женщины"
    if "Женщины" in title_lower or "жен " in title_lower or title_lower.endswith("жен"):
        return "Женщины"

    # Мужские категории
    if "юниор" in title_lower: # юниоры (проверяем после юниорок)
        return "Мужчины"
    if "юнош" in title_lower or "мальчик" in title_lower: # , мальчики
        return "Мужчины"
    if "мужчин" in title_lower or "муж " in title_lower or title_lower.endswith("муж"):
        return "Мужчины"

    return "Женщины" # Если категория не найдена

def normalize_distance(title: str) -> str:
    """Нормализует дистанцию (100м, 100 метров, 4х100)."""
    # Ищем эстафеты 4х100
    relay_match = re.search(r'4\s*[хx]\s*(\d+)', title)
    if relay_match:
        return f"4х{relay_match.group(1)} м"

    # Ищем обычные дистанции 50, 100, 200...
    dist_match = re.search(r'(\d+)\s*(?:м|метров|м\.)', title)
    if dist_match:
        return f"{dist_match.group(1)} м"

    return None

def is_relay_event(event_name: str) -> bool:
    """
    Проверяет, является ли дисциплина эстафетой.
    """
    if not event_name:
        return False

    event_lower = event_name.lower()

    # Признаки эстафеты
    relay_indicators = [
        'эстафет',
        '4x',           # 4x100
        '4х',           # 4х100 (кириллическая x)
        '4 x',          # 4 x 100
        '4 х',          # 4 х 100
    ]

    return any(indicator in event_lower for indicator in relay_indicators)


def get_discipline_from_event_name(event_name: str) -> str:
    """
    Определяет тип дисциплины для функции get_rank на основе названия события.

    Возвращает:
        'ласты' - плавание в ластах
        'классика' - плавание в классических ластах
        'подводное' - подводное плавание (включая ныряние)
    """
    if not event_name:
        return 'ласты'

    event_lower = event_name.lower()

    if "классическ" in event_lower:
        return 'классика'
    elif "ныряние" in event_lower or "подводное" in event_lower:
        return 'подводное'
    elif "плавание" in event_lower and "ласт" in event_lower:
        return 'ласты'
    elif "плавание" in event_lower:
        return 'ласты'
    else:
        return 'ласты'


def calculate_rank_for_result(distance_obj, time_str: str) -> str:
    """
    Рассчитывает разряд спортсмена на основе дистанции и времени.

    Args:
        distance_obj: Объект Distance с полями gender, name, distance_meters
        time_str: Время в формате строки (например: "00:16,46" или "1.22.5")

    Returns:
        Строка с разрядом (например: "МС", "КМС", "1", "2 юн" и т.д.)
        или пустая строка если не удалось определить.
    """
    from .utils import parse_time_to_seconds, get_rank, get_discipline_from_event_name

    if not distance_obj or not time_str:
        return ""

    # Парсим время
    seconds = parse_time_to_seconds(time_str)
    if seconds is None:
        return ""

    # Определяем пол
    gender_map = {'M': 'мужчины', 'F': 'женщины', 'X': 'мужчины'}
    gender = gender_map.get(distance_obj.gender, 'мужчины')

    # Определяем дисциплину
    discipline = get_discipline_from_event_name(distance_obj.name)

    # Получаем дистанцию в метрах
    distance_meters = distance_obj.distance_meters

    # Рассчитываем разряд
    rank = get_rank(gender, discipline, distance_meters, seconds)

    return rank


# Экспортируем новые функции
__all__ = [
    'parse_time_to_seconds',
    'format_time',
    'get_points_by_place',
    'normalize_event_name',
    'is_event_header',
    'is_athlete_row',
    'normalize_line',
    'get_best_time',
    'clean_raw_text',
    'normalize_sport_type',
    'normalize_category',
    'normalize_distance',
    'is_relay_event',
    'get_discipline_from_event_name',
    'calculate_rank_for_result',
    'get_rank',
]

# def get_relay_leg_distance(event_name: str) -> int | None:
#     """
#     Извлекает дистанцию одного этапа эстафеты.
#     Например: "4x100" -> 100
#     """
#     if not event_name:
#         return None

#     # Ищем паттерн 4x100 или 4х100
#     match = re.search(r'4\s*[xх]\s*(\d+)', event_name)
#     if match:
#         return int(match.group(1))

#     return None
def get_rank(gender: str, discipline: str, distance: int, time_input) -> str:
    """
    Определяет разряд спортсмена на основе показанного результата.

    gender: 'мужчины' или 'женщины'
    discipline:
        'ласты_авто' - плавание в ластах (авто хронометраж)
        'ласты_классика' - плавание в классических ластах
        'подводное' - подводное плавание (включая ныряние)
    distance: дистанция в метрах (50, 100, 200, 400, 800, 1500)
    time_input: время в секундах (float/int) или строка "1.22.5", "3:03.0" и т.д.

    Возвращает строку с разрядом, например "МСМК", "КМС", "1 юн" и т.д.
    Если время не укладывается ни в один разряд — возвращает "Без разряда".
    """

    # Парсинг времени с использованием существующей функции
    if isinstance(time_input, str):
        seconds = parse_time_to_seconds(time_input)
        if seconds is None:
            return "Неверный формат времени"
    else:
        seconds = float(time_input)

    # Таблицы нормативов [МСМК, МС, КМС, 1, 2, 3, 1юн, 2юн, 3юн]
    # Значения в секундах (максимальное время для получения разряда)

    tables = {
        ('мужчины', 'ласты'): {
            50:   [15.8, 16.7, 17.5, 18.5, 20.1, 21.8, 24.0, 26.2, 28.2],
            100:  [35.5, 37.3, 39.2, 42.0, 45.7, 49.7, 54.3, 59.2, 64.2],
            200:  [82.5, 86.0, 90.7, 97.2, 106.2, 114.8, 126.7, 138.5, 149.2],
            400:  [183.0, 192.5, 200.2, 215.7, 232.7, 251.8, 280.0, 305.7, 330.2],
            800:  [393.0, 410.0, 433.7, 454.7, 503.2, 543.2, 590.4, 652.0, 705.2],
            1500: [760.0, 800.0, 836.0, 890.5, 970.2, 1050.0, None, None, None]
        },
        ('мужчины', 'классика'): {
            50:   [19.3, 20.2, 21.2, 22.9, 24.7, 26.3, 29.7, 32.1, 35.2],
            100:  [43.0, 44.4, 47.1, 50.7, 55.7, 60.2, 65.5, 71.5, 78.0],
            200:  [96.4, 100.5, 105.0, 113.7, 122.7, 132.8, 145.7, 160.2, 170.2],
            400:  [212.4, 222.5, 233.2, 247.2, 265.2, 285.2, 307.7, 330.7, 358.2]
        },
        ('мужчины', 'подводное'): {
            100:  [33.0, 34.5, 36.2, 39.9, 42.2, 45.9, 50.2, 54.9, 59.2],
            400:  [170.0, 179.0, 187.5, 201.0, 218.0, 236.5, None, None, None],
            50:   [14.7, 15.4, 16.2, 17.2, 18.7, 20.2, None, None, None]  # ныряние
        },
        ('женщины', 'ласты'): {
            50:   [18.0, 18.7, 19.7, 21.0, 22.9, 24.7, 27.0, 29.5, 32.2],
            100:  [39.9, 40.9, 43.7, 46.7, 50.5, 54.7, 59.7, 64.7, 69.7],
            200:  [90.7, 93.0, 100.5, 106.7, 115.2, 125.2, 139.0, 150.0, 160.2],
            400:  [198.0, 205.6, 217.2, 233.2, 250.2, 270.2, 297.2, 326.2, 350.2],
            800:  [423.8, 440.7, 466.7, 498.5, 540.0, 580.7, 630.7, 697.2, 750.0],
            1500: [819.0, 855.0, 896.2, 956.7, 1040.2, 1125.0, None, None, None]
        },
        ('женщины', 'классика'): {
            50:   [22.0, 23.2, 24.5, 26.2, 27.7, 30.3, 33.2, 36.2, 39.2],
            100:  [47.9, 50.0, 53.2, 57.0, 61.6, 67.4, 73.0, 79.0, 85.2],
            200:  [107.0, 111.0, 117.2, 126.7, 135.7, 147.0, 162.2, 176.7, 190.2],
            400:  [228.9, 239.5, 252.8, 268.2, 286.7, 306.2, 330.2, 358.2, 386.2]
        },
        ('женщины', 'подводное'): {
            100:  [36.0, 37.9, 39.7, 42.7, 46.2, 50.0, 54.7, 59.9, 64.9],
            400:  [185.0, 194.6, 203.0, 218.0, 235.7, 253.8, None, None, None],
            50:   [16.7, 17.3, 18.2, 19.3, 21.1, 22.9, None, None, None]  # ныряние
        }
    }

    key = (gender, discipline)
    if key not in tables:
        return "Неизвестная дисциплина"

    if distance not in tables[key]:
        return "Нет разряда"

    norms = tables[key][distance]
    ranks = ["МСМК", "МС", "КМС", "1", "2", "3", "1 юн", "2 юн", "3 юн"]

    for i, norm in enumerate(norms):
        if norm is None:
            continue
        if seconds <= norm:
            return ranks[i]

    return "Без разряда"