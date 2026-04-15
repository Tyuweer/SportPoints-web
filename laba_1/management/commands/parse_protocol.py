# =============================================================================
# КОМАНДА ДЛЯ ПАРСИНГА ПРОТОКОЛОВ СОРЕВНОВАНИЙ
# =============================================================================
# Использование:
#   python manage.py parse_protocol <ID_СОРЕВНОВАНИЯ> --parser-type "<ТИП>"
#
# Примеры:
#   python manage.py parse_protocol 4 --parser-type "Всероссийские соревнования"
#   python manage.py parse_protocol 5 --parser-type "Кубок Сибири" --manual
# =============================================================================

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
    help = 'Парсит протокол соревнования и сохраняет результаты в БД'
    
    def add_arguments(self, parser):
        """
        Настройка аргументов командной строки
        """
        parser.add_argument(
            'competition_id',
            type=int,
            help='ID соревнования в базе данных (например: 4, 5, 6)'
        )
        parser.add_argument(
            '--parser-type',
            type=str,
            required=True,
            help='Тип парсера (ключ из PARSERS: "Всероссийские соревнования", "Кубок Сибири" и т.д.)'
        )
        parser.add_argument(
            '--manual',
            action='store_true',
            help='Использовать ручной хронометраж (+0.2 сек к результатам)'
        )
    
    def handle(self, *args, **options):
        """
        Основная логика команды
        """
        competition_id = options['competition_id']
        parser_type = options['parser_type']
        is_manual = options['manual']
        
        # =====================================================================
        # ШАГ 1: Находим соревнование в БД
        # =====================================================================
        try:
            competition = Competition.objects.get(id=competition_id)
        except Competition.DoesNotExist:
            self.stdout.write(self.style.ERROR(
                f'❌ Соревнование с ID {competition_id} не найдено!'
            ))
            self.stdout.write(self.style.WARNING(
                f'💡 Доступные соревнования:'
            ))
            for c in Competition.objects.all().order_by('-date'):
                self.stdout.write(f'   ID {c.id}: {c.name} ({c.date})')
            return
        
        self.stdout.write(self.style.HTTP_INFO('\n' + '='*60))
        self.stdout.write(self.style.HTTP_INFO(f'📋 ПАРСИНГ ПРОТОКОЛА'))
        self.stdout.write(self.style.HTTP_INFO('='*60))
        self.stdout.write(f'   Соревнование: {competition.name}')
        self.stdout.write(f'   Дата: {competition.date}')
        self.stdout.write(f'   Файл: {competition.protocol_file.name if competition.protocol_file else "НЕТ ФАЙЛА"}')
        self.stdout.write(f'   Парсер: {parser_type}')
        self.stdout.write(f'   Хронометраж: {"Ручной (+0.2с)" if is_manual else "Автоматический"}')
        self.stdout.write(self.style.HTTP_INFO('='*60 + '\n'))
        
        # =====================================================================
        # ШАГ 2: Проверяем наличие PDF файла
        # =====================================================================
        if not competition.protocol_file:
            self.stdout.write(self.style.WARNING('⚠️  У соревнования нет загруженного PDF файла!'))
            self.stdout.write(self.style.WARNING('💡  Загрузите файл через админку: /admin/laba_1/competition/'))
            return
        
        # Проверяем, существует ли файл на диске
        pdf_path = Path(competition.protocol_file.path)
        if not pdf_path.exists():
            self.stdout.write(self.style.ERROR(f'❌ Файл не найден: {pdf_path}'))
            return
        
        # =====================================================================
        # ШАГ 3: Получаем парсер через фабрику
        # =====================================================================
        try:
            parser = get_parser_by_name(parser_type)
        except ValueError as e:
            self.stdout.write(self.style.ERROR(f'❌ {e}'))
            return
        
        # =====================================================================
        # ШАГ 4: Запускаем парсинг PDF
        # =====================================================================
        self.stdout.write('🔄 Запуск парсинга PDF...')
        try:
            events = parser.parse(pdf_path, is_manual=is_manual)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Ошибка парсинга: {e}'))
            return
        
        total_events = len(events)
        total_results = sum(len(event.get('results', [])) for event in events)
        
        self.stdout.write(self.style.SUCCESS(f'✅ Парсинг завершён!'))
        self.stdout.write(f'   📊 Найдено событий: {total_events}')
        self.stdout.write(f'   📊 Найдено результатов: {total_results}\n')
        
        # =====================================================================
        # ШАГ 5: Сохраняем данные в БД (в транзакции)
        # =====================================================================
        self.stdout.write('💾 Сохранение данных в БД...')
        
        with transaction.atomic():
            saved_athletes = set()  # Множество для подсчёта уникальных спортсменов
            saved_results = 0
            skipped_no_distance = 0
            skipped_no_result = 0
            skipped_other = 0
            
            for event in events:
                event_name = event.get('event_name', 'Без названия')
                is_relay = event.get('relay', False)
                
                # -------------------------------------------------------------
                # 5.1: Находим дистанцию в справочнике (НЕ создаём новую!)
                # -------------------------------------------------------------
                distance = self._get_distance_from_reference(event_name, is_relay)
                
                if distance is None:
                    skipped_no_distance += len(event.get('results', []))
                    continue
                
                # -------------------------------------------------------------
                # 5.2: Сохраняем результаты спортсменов
                # -------------------------------------------------------------
                for res_data in event.get('results', []):
                    # Пропускаем, если нет времени
                    result_time = res_data.get('best_Result') or res_data.get('result')
                    if not result_time:
                        skipped_no_result += 1
                        continue
                    
                    # Находим или создаём спортсмена
                    athlete = self._get_or_create_athlete(res_data)
                    if athlete:
                        saved_athletes.add(athlete.id)
                    
                    # Сохраняем результат
                    result = self._save_result(athlete, competition, distance, res_data)
                    if result:
                        saved_results += 1
                    else:
                        skipped_other += 1
            
            # =================================================================
            # ШАГ 6: Выводим итоги
            # =================================================================
            self.stdout.write(self.style.SUCCESS('\n🎉 ПАРАСИНГ ЗАВЕРШЁН УСПЕШНО!'))
            self.stdout.write(self.style.HTTP_INFO('='*60))
            self.stdout.write(f'📊 СТАТИСТИКА:')
            self.stdout.write(f'   • Спортсменов добавлено/найдено: {len(saved_athletes)}')
            self.stdout.write(f'   • Результатов сохранено: {saved_results}')
            self.stdout.write(f'   • Пропущено (нет дистанции): {skipped_no_distance}')
            self.stdout.write(f'   • Пропущено (нет результата): {skipped_no_result}')
            self.stdout.write(f'   • Пропущено (прочее): {skipped_other}')
            self.stdout.write(self.style.HTTP_INFO('='*60))
            self.stdout.write(f'🏁 Соревнование: {competition.name} (ID: {competition.id})')
            self.stdout.write(self.style.HTTP_INFO('='*60 + '\n'))
            
            # Предупреждение, если ничего не сохранено
            if saved_results == 0:
                self.stdout.write(self.style.WARNING('⚠️  ВНИМАНИЕ: Ни один результат не был сохранён!'))
                self.stdout.write(self.style.WARNING('💡  Возможные причины:'))
                self.stdout.write(self.style.WARNING('   • Дистанции из протокола не найдены в справочнике'))
                self.stdout.write(self.style.WARNING('   • Парсер не смог извлечь данные из PDF'))
                self.stdout.write(self.style.WARNING('   • Неправильно выбран тип парсера (--parser-type)'))
    
    # =========================================================================
    # ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ
    # =========================================================================
    
    def _get_distance_from_reference(self, event_name: str, is_relay: bool) -> Distance | None:
        """
        Ищет дистанцию в фиксированном справочнике.
        НЕ создаёт новые записи!
        
        Args:
            event_name: Название события (например: "Плавание в ластах - 100 м Мужчины")
            is_relay: Флаг эстафеты
            
        Returns:
            Distance объект или None, если не найдено
        """
        # Парсим название события
        sport = normalize_sport_type(event_name)
        distance_str = normalize_distance(event_name)
        category = normalize_category(event_name)
        
        # Определяем пол
        gender_map = {'Мужчины': 'M', 'Женщины': 'F', 'Смешанная': 'X'}
        gender = gender_map.get(category, 'F')
        
        # Извлекаем метры
        meters = 0
        if 'м' in distance_str:
            relay_match = re.search(r'4\s*[хx]\s*(\d+)', distance_str)
            if relay_match:
                meters = int(relay_match.group(1))
            else:
                meters_str = distance_str.replace(' м', '').replace('м', '').strip()
                if meters_str.isdigit():
                    meters = int(meters_str)
        
        # Формируем базовое название для поиска
        base_name = sport if is_relay else f"{sport} - {distance_str}"
        
        # Ищем в справочнике
        try:
            distance = Distance.objects.get(
                name=base_name,
                gender=gender,
                is_relay=is_relay
            )
            return distance
        except Distance.DoesNotExist:
            self.stdout.write(self.style.WARNING(
                f'⚠️  Дистанция не найдена: "{base_name}" ({gender})'
            ))
            return None
    
    def _get_or_create_athlete(self, res_data: dict) -> Athlete | None:
        """
        Находит или создаёт спортсмена в БД.
        
        Args:
            res_data: Словарь с данными результата из парсера
            
        Returns:
            Athlete объект или None
        """
        full_name = res_data.get('full_name', '').strip()
        birth_year = res_data.get('birth_year')
        team = res_data.get('team', '')
        
        if not full_name:
            return None
        
        # Преобразуем год рождения в int
        if birth_year:
            try:
                birth_year = int(birth_year)
            except (ValueError, TypeError):
                birth_year = None
        
        # Ищем или создаём
        athlete, created = Athlete.objects.get_or_create(
            full_name=full_name,
            birth_year=birth_year,
            defaults={
                'team': team,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'   + Спортсмен: {full_name} ({birth_year or "?"})'))
        
        return athlete
    
    def _save_result(self, athlete: Athlete, competition: Competition, 
                     distance: Distance, res_data: dict) -> Result | None:
        """
        Сохраняет результат в БД.
        
        Args:
            athlete: Объект спортсмена
            competition: Объект соревнования
            distance: Объект дистанции
            res_data: Словарь с данными результата из парсера
            
        Returns:
            Result объект или None
        """
        # Проверяем, что дистанция найдена
        if distance is None:
            return None
        
        # Получаем лучший результат (с учётом регистра ключа!)
        result_time = res_data.get('best_Result') or res_data.get('result')
        
        # Пропускаем, если нет результата
        if not result_time:
            return None
        
        try:
            # Получаем очки (гарантируем, что это число)
            points_value = res_data.get('points', 0)
            if points_value is None or points_value == 'лично':
                points_value = 0
            elif isinstance(points_value, str):
                try:
                    points_value = int(points_value)
                except (ValueError, TypeError):
                    points_value = 0
            
            # Создаём или обновляем результат
            result, created = Result.objects.update_or_create(
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
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'   ❌ Ошибка сохранения {res_data.get("full_name", "Неизвестно")}: {e}'
            ))
            return None