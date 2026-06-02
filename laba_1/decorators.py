"""
Декораторы для проверки групп пользователей
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden


def group_required(*allowed_groups):
    """
    Декоратор для проверки группы пользователя
    Использование:
        @group_required('coach', 'admin')
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            if not hasattr(request.user, 'profile') or not request.user.profile.group:
                messages.error(request, 'Ваша группа пользователя не установлена')
                return redirect('profile')
            
            user_group = request.user.profile.group.name
            
            if user_group not in allowed_groups:
                messages.error(request, f'У вас нет прав для выполнения этого действия. Требуется группа: {", ".join(allowed_groups)}')
                return redirect('athlete_list')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def admin_required(view_func):
    """Декоратор для проверки администратора"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if not request.user.is_staff and not request.user.is_superuser:
            # Альтернатива - проверяем группу
            if not hasattr(request.user, 'profile') or not request.user.profile.group or request.user.profile.group.name != 'admin':
                messages.error(request, 'Требуется доступ администратора')
                return redirect('athlete_list')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def moderator_required(view_func):
    """Декоратор для проверки модератора"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if not hasattr(request.user, 'profile') or not request.user.profile.group:
            messages.error(request, 'Ваша группа пользователя не установлена')
            return redirect('profile')
        
        user_group = request.user.profile.group.name
        
        if user_group not in ['moderator', 'admin']:
            messages.error(request, 'Требуется доступ модератора или администратора')
            return redirect('athlete_list')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def coach_or_higher(view_func):
    """Декоратор для проверки тренера или выше"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if not hasattr(request.user, 'profile') or not request.user.profile.group:
            messages.error(request, 'Ваша группа пользователя не установлена')
            return redirect('profile')
        
        user_group = request.user.profile.group.name
        
        if user_group not in ['coach', 'moderator', 'admin']:
            messages.error(request, 'Требуется доступ тренера или выше')
            return redirect('athlete_list')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def athlete_or_higher(view_func):
    """Декоратор для проверки спортсмена или выше"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if not hasattr(request.user, 'profile') or not request.user.profile.group:
            messages.error(request, 'Ваша группа пользователя не установлена')
            return redirect('profile')
        
        user_group = request.user.profile.group.name
        
        if user_group not in ['athlete', 'coach', 'moderator', 'admin']:
            messages.error(request, 'Требуется быть зарегистрированным пользователем')
            return redirect('athlete_list')
        
        return view_func(request, *args, **kwargs)
    return wrapper
