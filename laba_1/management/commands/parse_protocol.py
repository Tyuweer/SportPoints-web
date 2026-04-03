from django.core.management.base import BaseCommand
from django.db import transaction
from pathlib import Path

from laba_1.models import Competition, Distance, Athlete, Result
from laba_1.parsers.factory import get_parser_by_name


class Command(BaseCommand):
    help = 'Парсит протокол соревнования и сохраняет результаты в БД'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'competition_id',
            type=int,
            help='ID соревнования в базе данных'
        )
        parser.add_argument(
            '--parser-type',
            type=str,
            required=True,
            help='Тип парсера (ключ из PARSERS: "Кубок края", "День спринтера" и т.д.)'
        )
        parser.add_argument(
            '--manual',
            action='store_true',
            help='Использовать ручной хронометраж (+0.2 сек к результатам)'
        )
    
    def handle(self, *args, **options):
        competition_id = options['competition_id']
        parser_type = options['parser_type']
        is_manual = options['manual']
        
        # 1. Находим соревнование
        try:
            competition = Competition.objects.get(id=competition_id)
        except Competition.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'❌ Соревнование с ID {competition_id} не найдено'))
            return
        
        self.stdout.write(f'📋 Парсим: {competition.name}')
        self.stdout.write(f'🔧 Парсер: {parser_type}')
        
        # 2. Проверяем файл
        if not competition.protocol_file:
            self.stdout.write(self.style.WARNING('⚠️ Нет загруженного PDF файла'))
            self.stdout.write('💡 Загрузите файл через админку')
            return
        
        # 3. Получаем парсер через фабрику
        try:
            parser = get_parser_by_name(parser_type)
        except ValueError as e:
            self.stdout.write(self.style.ERROR(f'❌ {e}'))
            return
        
        # 4. Запускаем парсинг
        self.stdout.write('🔄 Запуск парсинга...')
        events = parser.parse(Path(competition.protocol_file.path), is_manual=is_manual)
        self.stdout.write(f'✅ Найдено событий: {len(events)}')
        
        # 5. Сохраняем в БД
        with transaction.atomic():
            saved_athletes = 0
            saved_results = 0
            
            for event in events:
                # === Сохраняем дистанцию ===
                # event_name уже нормализован: "Плавание в ластах - 100 м Мужчины"
                distance = self._get_or_create_distance(event['event_name'], event.get('relay', False))
                
                # === Сохраняем результаты ===
                for res_data in event['results']:
                    athlete = self._get_or_create_athlete(res_data)
                    result = self._save_result(athlete, competition, distance, res_data)
                    
                    if result:
                        saved_results += 1
            
            saved_athletes = Athlete.objects.filter(
                results__competition=competition
            ).distinct().count()
        
        # 6. Итог
        self.stdout.write(self.style.SUCCESS(f'''
🎉 Парсинг завершён!
📊 Сохранено:
• Спортсменов: {saved_athletes}
• Результатов: {saved_results}
🏁 Соревнование: {competition.name}
        '''))
    
    def _get_or_create_distance(self, event_name: str, is_relay: bool) -> Distance:
        """
        Извлекает параметры дистанции из event_name и находит/создаёт запись.
        
        event_name формат: "Плавание в ластах - 100 м Мужчины"
        """
        from laba_1.utils.parsing import normalize_sport_type, normalize_distance, normalize_category
        
        # Парсим название
        sport = normalize_sport_type(event_name)
        distance_str = normalize_distance(event_name)
        category = normalize_category(event_name)
        
        # Определяем пол
        gender_map = {'Мужчины': 'M', 'Женщины': 'F', 'Смешанная': 'X'}
        gender = gender_map.get(category, 'F')  # По умолчанию женщины
        
        # Извлекаем метры из строки "100 м"
        # Извлекаем метры из строки "100 м" или "4х100 м"
        import re
        meters = 0
        if 'м' in distance_str:
            # Для эстафет извлекаем число после "4х" или "4x"
            relay_match = re.search(r'4\s*[хx]\s*(\d+)', distance_str)
            if relay_match:
                meters = int(relay_match.group(1))  # Для "4х100" возьмёт 100
            else:
                # Для обычных дистанций
                meters_str = distance_str.replace(' м', '').replace('м', '').strip()
                if meters_str.isdigit():
                    meters = int(meters_str)
        
        # Для эстафет корректируем название
        base_name = sport if is_relay else f"{sport} - {distance_str}"
        
        distance, _ = Distance.objects.get_or_create(
            name=base_name,
            gender=gender,
            defaults={
                'distance_meters': meters,
                'is_relay': is_relay,
            }
        )
        return distance
    
    def _get_or_create_athlete(self, res_data: dict) -> Athlete:
        """Находит или создаёт спортсмена"""
        athlete, _ = Athlete.objects.get_or_create(
            full_name=res_data['full_name'],
            birth_year=res_data.get('birth_year'),
            defaults={
                'team': res_data.get('team', ''),
            }
        )
        return athlete
    
    def _save_result(self, athlete: Athlete, competition: Competition, 
                    distance: Distance, res_data: dict) -> Result | None:
        """Сохраняет результат в БД"""

            # Пропускаем, если нет результата (DNS, DSQ, DNF без времени)
        if not res_data.get('result'):
            self.stdout.write(self.style.WARNING(
                f'⚠️ Пропущен результат без времени: {res_data.get("full_name", "Неизвестно")}'
            ))
            return None
        try:
            result, _ = Result.objects.update_or_create(
                athlete=athlete,
                competition=competition,
                distance=distance,
                defaults={
                    'place': res_data.get('place'),
                    'rank': res_data.get('rank'),
                    'result_time': res_data.get('result', ''),
                    'final_result': res_data.get('final_Result'),
                    'best_result': res_data.get('best_Result'),
                    'normative': res_data.get('normative'),
                    'points': res_data.get('points', 0),
                    'is_relay': res_data.get('relay', False),
                    'is_manual_timing': res_data.get('is_manual_timing', False),
                }
            )
            return result
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Ошибка сохранения: {e}'))
            return None