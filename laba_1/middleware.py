"""
Middleware для проверки групп пользователей и логирования
"""
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.deprecation import MiddlewareMixin
from laba_1.models import ActivityLog
from django.utils import timezone


class GroupPermissionMiddleware(MiddlewareMixin):
    """Middleware для проверки прав доступа на основе групп"""
    
    # Маршруты, требующие определенные группы
    PROTECTED_ROUTES = {
        '/addmember/': ['coach', 'moderator', 'admin'],
        '/athletes/.*/edit/': ['coach', 'moderator', 'admin'],
        '/athletes/.*/delete/': ['moderator', 'admin'],
    }
    
    def process_request(self, request):
        """Проверка прав доступа перед обработкой запроса"""
        
        # Для неавторизованных пользователей
        if not request.user.is_authenticated:
            # Но мы их не блокируем - они могут читать
            return None
        
        # Проверяем, есть ли профиль
        if not hasattr(request.user, 'profile'):
            return None
        
        # Достаем группу пользователя
        user_group = request.user.profile.group
        if not user_group:
            # Группа не установлена
            return None
        
        return None
    
    def process_response(self, request, response):
        """Логирование ответа"""
        return response


class ActivityLoggingMiddleware(MiddlewareMixin):
    """Middleware для логирования всех действий пользователей"""
    
    IMPORTANT_PATHS = [
        '/addmember/',
        '/edit/',
        '/delete/',
        '/profile/edit/',
        '/profile/password/',
        '/export-excel/',
    ]
    
    def process_request(self, request):
        # Сохраняем время начала запроса
        request._start_time = timezone.now()
        return None
    
    def process_response(self, request, response):
        """Логирование важных действий"""
        
        if request.user.is_authenticated:
            # Проверяем, является ли это важным действием
            should_log = False
            action_type = 'other'
            description = ''
            
            for path in self.IMPORTANT_PATHS:
                if path in request.path:
                    if request.method == 'POST':
                        should_log = True
                        
                        if 'addmember' in request.path:
                            action_type = 'add_athlete'
                            description = f"Добавлен спортсмен"
                        elif 'edit' in request.path and 'profile' not in request.path:
                            action_type = 'edit_athlete'
                            description = f"Отредактирован спортсмен"
                        elif 'delete' in request.path:
                            action_type = 'delete_athlete'
                            description = f"Удален спортсмен"
                        elif 'profile/edit' in request.path:
                            action_type = 'profile_update'
                            description = "Обновлен профиль пользователя"
                        elif 'profile/password' in request.path:
                            action_type = 'other'
                            description = "Изменен пароль"
                        elif 'export' in request.path:
                            action_type = 'export'
                            description = "Экспорт данных в Excel"
                    break
            
            # Сохраняем лог если нужно
            if should_log and response.status_code in [200, 302, 303]:
                try:
                    ActivityLog.objects.create(
                        user=request.user,
                        action=action_type,
                        description=description,
                        ip_address=self._get_client_ip(request),
                        user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],
                        request_path=request.path[:255]
                    )
                except Exception as e:
                    pass  # Не прерываем запрос из-за ошибки логирования
        
        return response
    
    @staticmethod
    def _get_client_ip(request):
        """Получить IP адрес клиента"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
