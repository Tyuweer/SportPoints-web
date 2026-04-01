from django.core.management.base import BaseCommand
from laba_1.models import Distance


class Command(BaseCommand):
    help = 'Заполняет справочник дистанций (34 дистанции)'
    
    def handle(self, *args, **kwargs):
        # Список всех дистанций
        # Формат: {'name': 'Название', 'gender': 'M/F/X', 'meters': расстояние, 'relay': True/False}
        
        distances_data = []
        
        # ==========================================
        # ПЛАВАНИЕ В ЛАСТАХ (обычные)
        # ==========================================
        swimming_distances = [50, 100, 200, 400, 800, 1500]
        
        for meters in swimming_distances:
            # Мужчины
            distances_data.append({
                'name': f'Плавание в ластах - {meters}',
                'gender': 'M',
                'meters': meters,
                'relay': False
            })
            # Женщины
            distances_data.append({
                'name': f'Плавание в ластах - {meters}',
                'gender': 'F',
                'meters': meters,
                'relay': False
            })
        
        # ==========================================
        # ПЛАВАНИЕ В КЛАССИЧЕСКИХ ЛАСТАХ
        # ==========================================
        classic_distances = [50, 100, 200, 400]
        
        for meters in classic_distances:
            # Мужчины
            distances_data.append({
                'name': f'Плавание в классических ластах - {meters}',
                'gender': 'M',
                'meters': meters,
                'relay': False
            })
            # Женщины
            distances_data.append({
                'name': f'Плавание в классических ластах - {meters}',
                'gender': 'F',
                'meters': meters,
                'relay': False
            })
        
        # ==========================================
        # ПОДВОДНОЕ ПЛАВАНИЕ
        # ==========================================
        underwater_distances = [50, 100, 200, 400]
        
        for meters in underwater_distances:
            # Мужчины
            distances_data.append({
                'name': f'Подводное плавание - {meters}',
                'gender': 'M',
                'meters': meters,
                'relay': False
            })
            # Женщины
            distances_data.append({
                'name': f'Подводное плавание - {meters}',
                'gender': 'F',
                'meters': meters,
                'relay': False
            })
        
        # ==========================================
        # ЭСТАФЕТЫ (обычные)
        # ==========================================
        # 4x100 и 4x200 - для мужчин и женщин отдельно
        relay_distances = [
            {'name': 'Плавание в ластах - 4x100', 'meters': 400},
            {'name': 'Плавание в ластах - 4x200', 'meters': 800},
        ]
        
        for relay in relay_distances:
            # Мужчины
            distances_data.append({
                'name': relay['name'],
                'gender': 'M',
                'meters': relay['meters'],
                'relay': True
            })
            # Женщины
            distances_data.append({
                'name': relay['name'],
                'gender': 'F',
                'meters': relay['meters'],
                'relay': True
            })
        
        # ==========================================
        # СМЕШАННЫЕ ЭСТАФЕТЫ
        # ==========================================
        mixed_relays = [
            {'name': 'Плавание в ластах - 4x50', 'meters': 200},
            {'name': 'Плавание в классических ластах - 4x100', 'meters': 400},
        ]
        
        for mixed in mixed_relays:
            # Смешанная (X = mixed)
            distances_data.append({
                'name': mixed['name'],
                'gender': 'X',  # X = смешанная
                'meters': mixed['meters'],
                'relay': True
            })
        
        # ==========================================
        # СОЗДАЕМ ДИСТАНЦИИ В БД
        # ==========================================
        created_count = 0
        updated_count = 0
        
        for d in distances_data:
            # get_or_create возвращает (объект, создан_ли_он)
            obj, created = Distance.objects.get_or_create(
                name=d['name'],
                gender=d['gender'],
                defaults={
                    'distance_meters': d['meters'],
                    'is_relay': d['relay'],
                }
            )
            
            if created:
                created_count += 1
            else:
                updated_count += 1
        
        # Выводим результат
        self.stdout.write(self.style.SUCCESS(f'\n✅ Готово!'))
        self.stdout.write(self.style.SUCCESS(f'   Создано дистанций: {created_count}'))
        self.stdout.write(self.style.SUCCESS(f'   Уже существовало: {updated_count}'))
        self.stdout.write(self.style.SUCCESS(f'   Всего в базе: {Distance.objects.count()}\n'))
        
        # Показываем список
        self.stdout.write(self.style.HTTP_INFO('📋 Список дистанций:'))
        for d in Distance.objects.all().order_by('distance_meters', 'name'):
            gender_label = {'M': 'Мужчины', 'F': 'Женщины', 'X': 'Смешанная'}.get(d.gender, d.gender)
            relay_mark = '🏊‍♂️' if d.is_relay else ''
            self.stdout.write(f'   {d.distance_meters}м | {d.name} ({gender_label}) {relay_mark}')