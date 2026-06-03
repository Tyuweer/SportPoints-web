# laba_1/middleware.py
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.deprecation import MiddlewareMixin
from laba_1.models import ActivityLog
from django.utils import timezone
import re


class GroupPermissionMiddleware(MiddlewareMixin):
    def get_user_group(self, request):
        
        if not request.user.is_authenticated:
            return 'viewer'
        
        # Суперпользователи считаются админами
        if request.user.is_superuser or request.user.is_staff:
            return 'admin'
        
        # Проверяем профиль и группу
        if hasattr(request.user, 'profile') and request.user.profile.group:
            # Получаем объект группы
            group_obj = request.user.profile.group
            
            # Извлекаем name из объекта (это строка 'Coach', 'admin' и т.д.)
            group_name = group_obj.name  # <-- ВАЖНО! Берем поле name
            
            print(f"DEBUG: User={request.user}, Group object={group_obj}, Group name={group_name}")
            
            return group_name
        
        return 'Authorized'
    
    def process_request(self, request):
        """Основной метод проверки доступа"""
        
        # Пропускаем статические и медиа файлы
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return None
        
        # Пропускаем Django admin
        if request.path.startswith('/admin/'):
            return None
        
        # Получаем группу пользователя
        user_group = self.get_user_group(request)
        
        # Получаем путь
        path = request.path
        
        # ============ ПУБЛИЧНЫЕ МАРШРУТЫ (доступны всем) ============
        public_routes = [
            '/register/',
            '/login/',
            '/confirm-email/',
            '/competitions/',
        ]
        
        for route in public_routes:
            if path.startswith(route):
                return None
        
        # Список спортсменов - доступен всем
        if path == '/' or path == '/athlete_list/' or path.startswith('/athletes?'):
            return None
        
        # Просмотр деталей спортсмена - доступен всем
        if re.match(r'^/athletes/\d+/$', path):
            return None
        
        # ============ МАРШРУТЫ ДЛЯ АВТОРИЗОВАННЫХ ============
        authorized_routes = [ 
            '/profile/',
            '/profile/edit/',
            '/profile/password/',
            '/profile/activity/',
            '/calc',
            '/calculate/',
            '/export-excel/',
            '/register-competition/',
            '/logout/',
        ]
        
        for route in authorized_routes:
            if path.startswith(route) or path == route:
                if user_group == 'viewer':
                    messages.error(request, "Для доступа к этой странице необходимо авторизоваться.")
                    return redirect('login')
                return None
        
        # ============ МАРШРУТЫ ДЛЯ ТРЕНЕРА И ВЫШЕ (добавление и редактирование) ============
        # Добавление спортсмена
        if path == '/addmember/':
            if user_group not in ['Coach', 'admin']:
                messages.error(request, "У вас недостаточно прав для добавления спортсменов.")
                return redirect('athlete_list')
            return None
        
        # Редактирование спортсмена
        if re.match(r'^/athletes/\d+/edit/$', path):
            if user_group not in ['Coach', 'admin']:
                messages.error(request, "У вас недостаточно прав для редактирования спортсменов.")
                return redirect('athlete_list')
            return None
        
        # ============ МАРШРУТЫ ТОЛЬКО ДЛЯ АДМИНА (удаление) ============
        if re.match(r'^/athletes/\d+/delete/$', path) or re.match(r'^/athletes/delete-ajax/\d+/$', path):
            if user_group != 'admin':
                messages.error(request, "Только администратор может удалять спортсменов.")
                return redirect('athlete_list')
            return None
        
        # ============ ВСЕ ОСТАЛЬНЫЕ МАРШРУТЫ ============
        # По умолчанию - доступ только админу
        if user_group != 'admin':
            messages.error(request, "Доступ запрещен. У вас недостаточно прав.")
            return redirect('athlete_list')
        
        return None


class ActivityLoggingMiddleware(MiddlewareMixin):
    """Middleware для логирования действий пользователей"""
    
    IMPORTANT_PATHS = [
        '/addmember/',
        '/add_member/',
        '/edit/',
        '/delete/',
        '/profile/edit/',
        '/profile/password/',
        '/password_change/',
        '/export-excel/',
        '/export/',
        '/register/',
        '/login/',
    ]
    
    def process_request(self, request):
        request._start_time = timezone.now()
        return None
    
    def process_response(self, request, response):
        
        if request.user.is_authenticated:
            path = request.path
            should_log = False
            action_type = 'other'
            description = ''
            
            # Логируем добавление спортсмена
            if path == '/addmember/' and request.method == 'POST':
                should_log = True
                action_type = 'add_athlete'
                description = f"Добавлен новый спортсмен"
            
            # Логируем редактирование спортсмена
            elif re.match(r'^/athletes/\d+/edit/$', path) and request.method == 'POST':
                should_log = True
                action_type = 'edit_athlete'
                description = f"Отредактирован спортсмен"
            
            # Логируем удаление спортсмена
            elif re.match(r'^/athletes/\d+/delete/$', path) or re.match(r'^/athletes/delete-ajax/\d+/$', path):
                if request.method == 'POST' or request.method == 'DELETE':
                    should_log = True
                    action_type = 'delete_athlete'
                    description = f"Удален спортсмен"
            
            # Логируем редактирование профиля
            elif path == '/profile/edit/' and request.method == 'POST':
                should_log = True
                action_type = 'profile_update'
                description = "Обновлен профиль пользователя"
            
            # Логируем смену пароля
            elif path == '/profile/password/' and request.method == 'POST':
                should_log = True
                action_type = 'password_change'
                description = "Изменен пароль"
            
            # Логируем экспорт в Excel
            elif path == '/export-excel/':
                should_log = True
                action_type = 'export'
                description = "Экспорт данных в Excel"
            
            # Логируем регистрацию на соревнования
            elif path == '/register-competition/' and request.method == 'POST':
                should_log = True
                action_type = 'competition_register'
                description = "Регистрация на соревнование"
            
            if should_log and response.status_code in [200, 302, 303, 201]:
                try:
                    ActivityLog.objects.create(
                        user=request.user,
                        action=action_type,
                        description=description,
                        ip_address=self._get_client_ip(request),
                        user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],
                        request_path=path[:255]
                    )
                except Exception as e:
                    print(f"Logging error: {e}")
        
        return response
    
    @staticmethod
    def _get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip 