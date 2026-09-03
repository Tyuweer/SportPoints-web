from django.core.management.base import BaseCommand
from laba_1.models import Distance

# для заполнения дистанций
class Command(BaseCommand):

    def handle(self, *args, **kwargs):

        Distance.objects.all().delete()
        
        distances_data = []

        swimming_distances = [50, 100, 200, 400, 800, 1500]
        
        for meters in swimming_distances:
            distances_data.append({
                'name': f'Плавание в ластах - {meters} м',
                'gender': 'M',
                'meters': meters,
                'relay': False
            })
            distances_data.append({
                'name': f'Плавание в ластах - {meters} м',
                'gender': 'F',
                'meters': meters,
                'relay': False
            })
        
        classic_distances = [50, 100, 200, 400]
        
        for meters in classic_distances:
            distances_data.append({
                'name': f'Плавание в классических ластах - {meters} м',
                'gender': 'M',
                'meters': meters,
                'relay': False
            })
            distances_data.append({
                'name': f'Плавание в классических ластах - {meters} м',
                'gender': 'F',
                'meters': meters,
                'relay': False
            })
        
        underwater_distances = [50, 100, 200, 400]
        
        for meters in underwater_distances:
            distances_data.append({
                'name': f'Подводное плавание - {meters} м',
                'gender': 'M',
                'meters': meters,
                'relay': False
            })
            distances_data.append({
                'name': f'Подводное плавание - {meters} м',
                'gender': 'F',
                'meters': meters,
                'relay': False
            })
        
        relay_distances = [
            {'name': 'Плавание в ластах - 4x100', 'meters': 400 },
            {'name': 'Плавание в ластах - 4x200', 'meters': 800},
        ]
        
        for relay in relay_distances:
            distances_data.append({
                'name': relay['name'],
                'gender': 'M',
                'meters': relay['meters'],
                'relay': True
            })
            distances_data.append({
                'name': relay['name'],
                'gender': 'F',
                'meters': relay['meters'],
                'relay': True
            })

        mixed_relays = [
            {'name': 'Плавание в ластах - 4x50', 'meters': 200},
            {'name': 'Плавание в классических ластах - 4x100', 'meters': 400},
        ]
        
        for mixed in mixed_relays:
            distances_data.append({
                'name': mixed['name'],
                'gender': 'X',
                'meters': mixed['meters'],
                'relay': True
            })

        created_count = 0
        
        for d in distances_data:
            Distance.objects.create(
                name=d['name'],
                gender=d['gender'],
                distance_meters=d['meters'],
                is_relay=d['relay']
            )
            created_count += 1
        