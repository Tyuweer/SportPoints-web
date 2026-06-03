# laba_1/management/commands/setup_groups.py
from django.core.management.base import BaseCommand
from laba_1.models import UserGroup

class Command(BaseCommand):
    help = 'Создает группы пользователей по умолчанию'
    
    def handle(self, *args, **kwargs):
        groups_data = [
            {'name': 'viewer', 'description': 'Просмотр (неавторизованный)'},
            {'name': 'Authorized', 'description': 'Пользователь'},
            {'name': 'Coach', 'description': 'Тренер'},
            {'name': 'admin', 'description': 'Администратор'},
        ]
        
        for group_data in groups_data:
            group, created = UserGroup.objects.get_or_create(
                name=group_data['name'],
                defaults={'description': group_data['description']}
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Создана группа: {group_data["description"]}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'✓ Группа уже существует: {group_data["description"]}')
                )
        
        self.stdout.write(self.style.SUCCESS('\n🎉 Все группы успешно созданы!'))