from django.core.management.base import BaseCommand
from django.db import transaction
from pathlib import Path
import re

from laba_1.models import Competition, Distance, Athlete, Result
from laba_1.parsers.factory import get_parser_by_name
from laba_1.core.utils import (
    normalize_sport_type,
    normalize_distance,
    normalize_category
)


class Command(BaseCommand):


    def add_arguments(self, parser):
        parser.add_argument('competition_id', type=int,)
        parser.add_argument('--parser-type', type=str,)
        parser.add_argument('--manual', action='store_true')

    def handle(self, *args, **options):
        competition_id = options['competition_id']
        parser_type = options['parser_type']
        is_manual = options['manual']

        competition = Competition.objects.get(id=competition_id)

        if not competition.protocol_file:
            self.stdout.write(self.style.ERROR('Нет PDF файла у соревнования'))
            return

        pdf_path = Path(competition.protocol_file.path)
        if not pdf_path.exists():
            self.stdout.write(self.style.ERROR(f'Файл не найден: {pdf_path}'))
            return

        parser = get_parser_by_name(parser_type)
        events = parser.parse(pdf_path, is_manual=is_manual)

        with transaction.atomic():
            for event in events:
                event_name = event.get('event_name', '')
                is_relay = event.get('relay', False)

                distance = self._get_distance(event_name, is_relay)
                if distance is None:
                    continue

                for res_data in event.get('results', []):
                    result_time = res_data.get('best_Result') or res_data.get('result')
                    if not result_time:
                        continue

                    athlete = self._get_or_create_athlete(res_data)
                    if athlete:
                        self._save_result(athlete, competition, distance, res_data)

        self.stdout.write(self.style.SUCCESS('Парсинг завершён'))

    def _get_distance(self, event_name: str, is_relay: bool) -> Distance | None:
        sport = normalize_sport_type(event_name)
        distance_str = normalize_distance(event_name)
        category = normalize_category(event_name)

        gender_map = {'Мужчины': 'M', 'Женщины': 'F', 'Смешанная': 'X'}
        gender = gender_map.get(category, 'F')

        base_name = sport if is_relay else f"{sport} - {distance_str}"

        try:
            return Distance.objects.get(name=base_name, gender=gender, is_relay=is_relay)
        except Distance.DoesNotExist:
            return None

    def _get_or_create_athlete(self, res_data: dict) -> Athlete | None:
        full_name = res_data.get('full_name', '').strip()
        birth_year = res_data.get('birth_year')
        team = res_data.get('team', '')

        if not full_name:
            return None

        parts = full_name.strip().split()
        if len(parts) >= 2:
            normalized_name = f"{parts[0]} {parts[1]}"
        elif len(parts) == 1:
            normalized_name = parts[0]
        else:
            return None

        if birth_year:
            try:
                birth_year = int(birth_year)
            except (ValueError, TypeError):
                birth_year = None

        athlete, _ = Athlete.objects.get_or_create(
            full_name=normalized_name,
            birth_year=birth_year,
            defaults={'team': team}
        )
        return athlete

    def _save_result(self, athlete: Athlete, competition: Competition,
                    distance: Distance, res_data: dict) -> Result | None:
        if distance is None:
            return None

        result_time = res_data.get('best_Result') or res_data.get('result')
        if not result_time:
            return None

        points_value = res_data.get('points', 0)
        if points_value is None or points_value == 'лично':
            points_value = 0
        elif isinstance(points_value, str):
            try:
                points_value = int(points_value)
            except (ValueError, TypeError):
                points_value = 0

        result, _ = Result.objects.update_or_create(
            athlete=athlete,
            competition=competition,
            distance=distance,
            defaults={
                'place': int(res_data.get('place') or 0) if res_data.get('place') else None,
                'rank': res_data.get('rank'),
                'result_time': result_time,
                'final_result': res_data.get('final_Result'),
                'best_result': res_data.get('best_Result'),
                'normative': res_data.get('normative'),
                'points': points_value,
                'is_manual_timing': res_data.get('is_manual_timing', False),
            }
        )
        return result