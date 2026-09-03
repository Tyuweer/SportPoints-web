from .base import IParser
from laba_1.parsers.kubok_rossii import KubokRossii_Parser
from laba_1.parsers.goldfins import Goldfins_Parser
from .krai_ocr_parser import KraiOcrParser

PARSERS: dict[str, type[IParser]] = {
    "Первенство Края": KubokRossii_Parser,
    "Кубок края": KubokRossii_Parser,
    "День спринтера": KubokRossii_Parser,
    "Всероссийские соревнования": KubokRossii_Parser,
    "Золотая Ласта": Goldfins_Parser,
    "Кубок Сибири": KubokRossii_Parser,
    "Чемпионат Края (OCR)": KraiOcrParser,
}


def get_parser_by_name(parser_name: str) -> IParser:
    """
    Возвращает экземпляр парсера по названию соревнования.
    """
    if parser_name not in PARSERS:
        available = ", ".join(PARSERS.keys())
        raise ValueError(
            f"Неизвестный тип соревнования: '{parser_name}'.\n"
            f"Доступные: {available}"
        )
    return PARSERS[parser_name]()