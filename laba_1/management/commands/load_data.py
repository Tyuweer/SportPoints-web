from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from laba_1.models import (
    UserGroup, UserProfile, Competition, Distance, Athlete, Result
)
from datetime import datetime, timedelta
import random


class Command(BaseCommand):
    help = 'Load initial data to the database'

    def handle(self, *args, **options):
        self.stdout.write('Starting data loading...')
        
        # Create user groups
        self.stdout.write('Creating user groups...')
        groups_data = [
            ('viewer', 'Просмотр (неавторизованный)'),
            ('athlete', 'Спортсмен (редактирование)'),
            ('coach', 'Тренер (расширенный доступ)'),
            ('moderator', 'Модератор'),
            ('admin', 'Администратор'),
        ]
        
        groups = {}
        for name, description in groups_data:
            group, _ = UserGroup.objects.get_or_create(
                name=name,
                defaults={'description': description}
            )
            groups[name] = group
        
        # Create users
        self.stdout.write('Creating users...')
        users = []
        user_credentials = [
            ('admin', 'admin@example.com', 'admin', 'admin', 'admin', 'admin'),
            ('coach1', 'coach1@example.com', 'Иван', 'Петров', 'coach1', 'coach1'),
            ('athlete1', 'athlete1@example.com', 'Сергей', 'Иванов', 'athlete1', 'athlete1'),
            ('athlete2', 'athlete2@example.com', 'Мария', 'Сидорова', 'athlete2', 'athlete2'),
            ('athlete3', 'athlete3@example.com', 'Петр', 'Никитин', 'athlete3', 'athlete3'),
        ]
        
        for username, email, first_name, last_name, username_pass, password in user_credentials:
            try:
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': email,
                        'first_name': first_name,
                        'last_name': last_name,
                    }
                )
                if created:
                    user.set_password(password)
                    user.save()
                
                # Assign group
                group_name = 'admin' if username == 'admin' else ('coach' if 'coach' in username else 'athlete')
                profile, _ = UserProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'group': groups[group_name],
                        'city': 'Москва',
                        'email_verified': True,
                    }
                )
                users.append(user)
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Error creating user {username}: {e}'))
        

        self.stdout.write(self.style.SUCCESS(f'Successfully loaded data!\n'))
        self.stdout.write(f'  ✓ Users created: {len(users)}')
        self.stdout.write(f'  ✓ Groups created: {len(groups)}')

