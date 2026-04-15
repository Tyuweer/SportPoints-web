from django import template
from laba_1.core.utils import get_points_by_place

register = template.Library()

@register.filter(name='points_by_place')
def points_by_place_filter(value):
    """
    Фильтр для получения очков по месту.
    Использование в шаблоне: {{ place|points_by_place }}
    """
    try:
        place = int(value)
        return get_points_by_place(place)
    except (ValueError, TypeError):
        return 0