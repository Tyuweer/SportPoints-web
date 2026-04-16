# РЕКОМЕНДАЦИИ ПО РАСШИРЕНИЮ ФУНКЦИОНАЛА
## для получения максимальной оценки (5+) и выполнения дополнительного задания

---

## 📋 ТЕКУЩЕЕ СОСТОЯНИЕ ПРОЕКТА

На основе анализа вашего кода выявлено:

### ✅ Уже реализовано:
- 4 основные модели данных (Competition, Distance, Athlete, Result)
- Архитектура MVT (Django)
- 7 страниц/переходов
- Формы для добавления данных пользователем
- ООП в коде
- HTML-клиент
- Шаблоны Django

### ⚠️ Требуется доработать для оценки «5»:

---

## 🔧 ПРИОРИТЕТНЫЕ ЗАДАЧИ (для оценки 5)

### 1. Переход на PostgreSQL

**Что сделать:**
```python
# В settings.py заменить:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'athlete_points_db',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

**Шаги:**
1. Установить PostgreSQL
2. Создать базу данных: `CREATE DATABASE athlete_points_db;`
3. Установить адаптер: `pip install psycopg2-binary`
4. Применить миграции: `python manage.py migrate`

---

### 2. Расширение модели пользователя (UserProfile)

**Файл:** `laba_1/models.py`

```python
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    USER_ROLE_CHOICES = [
        ('admin', 'Администратор'),
        ('coach', 'Тренер'),
        ('athlete', 'Спортсмен'),
        ('viewer', 'Наблюдатель'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField("Номер телефона", max_length=20, blank=True)
    avatar = models.ImageField("Аватар", upload_to='avatars/', blank=True, null=True)
    bio = models.TextField("О себе", blank=True)
    role = models.CharField("Роль", max_length=20, choices=USER_ROLE_CHOICES, default='viewer')
    email_verified = models.BooleanField("Email подтверждён", default=False)
    verification_token = models.CharField("Токен подтверждения", max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"
    
    def __str__(self):
        return f"Профиль {self.user.username}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
```

---

### 3. Группы пользователей с правами доступа

**Файл:** `laba_1/models.py`

```python
class UserGroup(models.Model):
    GROUP_CHOICES = [
        ('admin', 'Администратор'),
        ('coach', 'Тренер'),
        ('athlete', 'Спортсмен'),
    ]
    
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    can_add_athletes = models.BooleanField(default=False)
    can_edit_athletes = models.BooleanField(default=False)
    can_delete_athletes = models.BooleanField(default=False)
    can_view_analytics = models.BooleanField(default=False)
    can_upload_protocols = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name
```

**Файл:** `laba_1/decorators.py` (создать новый)

```python
from functools import wraps
from django.http import HttpResponseForbidden

def group_required(group_name):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return HttpResponseForbidden("Требуется авторизация")
            
            if hasattr(request.user, 'profile'):
                if request.user.profile.role != group_name and not request.user.is_superuser:
                    return HttpResponseForbidden("Недостаточно прав")
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
```

**Использование в views.py:**
```python
from .decorators import group_required

@group_required('coach')
def add_member(request):
    # Доступно только тренерам
    ...
```

---

### 4. Подтверждение регистрации через email (token-based)

**Файл:** `laba_1/models.py`

```python
import uuid
from datetime import timedelta
from django.utils import timezone

class EmailVerification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if not self.token:
            self.token = str(uuid.uuid4())
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)
    
    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at
```

**Файл:** `laba_1/views.py`

```python
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages

def register_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_active = False  # Деактивировать до подтверждения
        user.save()
        
        # Создать токен подтверждения
        verification = EmailVerification.objects.create(user=user)
        
        # Отправить email
        verification_link = f"http://yourdomain.com/verify/{verification.token}/"
        send_mail(
            'Подтверждение регистрации',
            f'Перейдите по ссылке для подтверждения: {verification_link}',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        
        messages.success(request, 'Письмо с подтверждением отправлено на ваш email')
        return redirect('login')
    
    return render(request, 'registration/register.html')

def verify_email(request, token):
    try:
        verification = EmailVerification.objects.get(token=token)
        if verification.is_valid():
            user = verification.user
            user.is_active = True
            user.save()
            verification.is_used = True
            verification.save()
            messages.success(request, 'Email успешно подтверждён! Теперь вы можете войти.')
            return redirect('login')
        else:
            messages.error(request, 'Ссылка недействительна или истекла')
    except EmailVerification.DoesNotExist:
        messages.error(request, 'Ссылка не найдена')
    
    return redirect('register')
```

---

### 5. Фильтрация и поиск записей

**Файл:** `laba_1/views.py`

```python
from django.db.models import Q

def athlete_list(request):
    query = request.GET.get('q', '')
    team_filter = request.GET.get('team', '')
    year_filter = request.GET.get('birth_year', '')
    tag_filter = request.GET.get('tag', '')
    
    athletes = Athlete.objects.filter(removed=False)
    
    # Поиск по ФИО
    if query:
        athletes = athletes.filter(Q(full_name__icontains=query))
    
    # Фильтр по команде
    if team_filter:
        athletes = athletes.filter(team__icontains=team_filter)
    
    # Фильтр по году рождения
    if year_filter:
        athletes = athletes.filter(birth_year=year_filter)
    
    # Пагинация
    from django.core.paginator import Paginator
    paginator = Paginator(athletes, 15)  # 15 записей на странице
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'athletes': page_obj,
        'query': query,
        'team_filter': team_filter,
        'year_filter': year_filter,
    }
    return render(request, 'athlete_list.html', context)
```

**Файл:** `laba_1/templates/laba_1/athlete_list.html`

```html
<!-- Форма поиска и фильтрации -->
<form method="get" class="filter-form">
    <input type="text" name="q" placeholder="Поиск по ФИО" value="{{ query }}">
    <input type="text" name="team" placeholder="Команда" value="{{ team_filter }}">
    <input type="number" name="birth_year" placeholder="Год рождения" value="{{ year_filter }}">
    <button type="submit">Найти</button>
</form>

<!-- Пагинация -->
<div class="pagination">
    {% if page_obj.has_previous %}
        <a href="?page=1">&laquo; Первая</a>
        <a href="?page={{ page_obj.previous_page_number }}">Пред.</a>
    {% endif %}
    
    <span>Страница {{ page_obj.number }} из {{ page_obj.paginator.num_pages }}</span>
    
    {% if page_obj.has_next %}
        <a href="?page={{ page_obj.next_page_number }}">След.</a>
        <a href="?page={{ page_obj.paginator.num_pages }}">Последняя &raquo;</a>
    {% endif %}
</div>
```

---

### 6. Кэширование (Cache)

**Файл:** `CSP_1/settings.py`

```python
# Добавить настройку кэша
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 300,  # 5 минут
    }
}

# Для production лучше использовать Redis:
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.redis.RedisCache',
#         'LOCATION': 'redis://127.0.0.1:6379/1',
#     }
# }
```

**Использование в views.py:**

```python
from django.core.cache import cache

def athlete_list(request):
    # Проверить кэш
    cache_key = f'athlete_list_{request.GET.urlencode()}'
    athletes = cache.get(cache_key)
    
    if athletes is None:
        # Если нет в кэше - выполнить запрос
        athletes = Athlete.objects.filter(removed=False)
        # Сохранить в кэш на 5 минут
        cache.set(cache_key, athletes, 300)
    
    # ... остальной код
```

---

### 7. Cookie

**Файл:** `laba_1/views.py`

```python
from django.http import HttpResponse

def set_theme_cookie(request):
    theme = request.GET.get('theme', 'light')
    response = HttpResponse(f"Тема установлена: {theme}")
    response.set_cookie('theme', theme, max_age=30*24*60*60)  # 30 дней
    return response

def athlete_list(request):
    # Получить тему из cookie
    theme = request.COOKIES.get('theme', 'light')
    
    context = {
        'theme': theme,
        # ... остальные данные
    }
    return render(request, 'athlete_list.html', context)
```

---

### 8. JavaScript элементы

**Файл:** `laba_1/static/laba_1/js/main.js` (создать)

```javascript
// Асинхронный поиск спортсменов
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('athlete-search');
    const resultsContainer = document.getElementById('search-results');
    
    if (searchInput) {
        let debounceTimer;
        searchInput.addEventListener('input', function(e) {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                const query = e.target.value;
                if (query.length >= 2) {
                    fetchAthletes(query);
                }
            }, 300);
        });
    }
    
    function fetchAthletes(query) {
        fetch(`/api/athletes/search/?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                displayResults(data);
            })
            .catch(error => console.error('Error:', error));
    }
    
    function displayResults(athletes) {
        resultsContainer.innerHTML = '';
        athletes.forEach(athlete => {
            const div = document.createElement('div');
            div.textContent = athlete.full_name;
            div.className = 'search-result-item';
            div.onclick = () => window.location.href = `/athletes/${athlete.id}/`;
            resultsContainer.appendChild(div);
        });
    }
});

// Переключение темы
function toggleTheme() {
    const currentTheme = document.body.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.body.setAttribute('data-theme', newTheme);
    document.cookie = `theme=${newTheme}; max-age=${30*24*60*60}; path=/`;
}
```

**API View для AJAX:**

**Файл:** `laba_1/views.py`

```python
from django.http import JsonResponse

def search_athletes_api(request):
    query = request.GET.get('q', '')
    athletes = Athlete.objects.filter(
        full_name__icontains=query,
        removed=False
    )[:10]  # Максимум 10 результатов
    
    data = [
        {'id': a.id, 'full_name': a.full_name, 'team': a.team}
        for a in athletes
    ]
    
    return JsonResponse(data, safe=False)
```

**Файл:** `laba_1/urls.py`

```python
urlpatterns = [
    # ... существующие URL
    path('api/athletes/search/', views.search_athletes_api, name='api_athlete_search'),
]
```

---

### 9. Личный кабинет пользователя

**Файл:** `laba_1/forms.py`

```python
from django import forms
from django.contrib.auth.models import User

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class ProfileExtraForm(forms.Form):
    phone = forms.CharField(max_length=20, required=False)
    bio = forms.CharField(widget=forms.Textarea, required=False)
```

**Файл:** `laba_1/views.py`

```python
from django.contrib.auth.decorators import login_required

@login_required
def user_profile(request):
    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, instance=request.user)
        profile_form = ProfileExtraForm(request.POST)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            
            profile = request.user.profile
            profile.phone = profile_form.cleaned_data['phone']
            profile.bio = profile_form.cleaned_data['bio']
            profile.save()
            
            messages.success(request, 'Профиль успешно обновлён')
            return redirect('profile')
    else:
        user_form = UserProfileForm(instance=request.user)
        profile = getattr(request.user, 'profile', None)
        profile_form = ProfileExtraForm(initial={
            'phone': profile.phone if profile else '',
            'bio': profile.bio if profile else '',
        })
    
    return render(request, 'profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })
```

---

### 10. Асинхронное программирование (дополнительное задание)

**Установка:**
```bash
pip install celery redis
```

**Файл:** `CSP_1/celery.py` (создать)

```python
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CSP_1.settings')

app = Celery('CSP_1')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
```

**Файл:** `CSP_1/settings.py`

```python
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
```

**Файл:** `laba_1/tasks.py` (создать)

```python
from celery import shared_task
from django.core.mail import send_mail
from .models import Competition

@shared_task
def send_competition_notification(competition_id, user_email):
    competition = Competition.objects.get(id=competition_id)
    send_mail(
        'Новое соревнование',
        f'Добавлено новое соревнование: {competition.name}',
        'noreply@example.com',
        [user_email],
        fail_silently=False,
    )
    return 'Notification sent'

@shared_task
def calculate_athlete_statistics(athlete_id):
    # Долгая операция расчёта статистики
    from .models import Athlete, Result
    athlete = Athlete.objects.get(id=athlete_id)
    results = Result.objects.filter(athlete=athlete)
    
    # Расчёты...
    total_points = sum(int(r.points) for r in results if r.points)
    
    return {'athlete_id': athlete_id, 'total_points': total_points}
```

**Использование в views.py:**

```python
from .tasks import send_competition_notification, calculate_athlete_statistics

def add_competition(request):
    if request.method == 'POST':
        competition = Competition.objects.create(...)
        
        # Асинхронная отправка уведомлений
        for user in get_subscribed_users():
            send_competition_notification.delay(competition.id, user.email)
        
        return redirect('competitions')
```

---

## 📊 ПЛАН ДЕЙСТВИЙ

### Этап 1: Базовые требования (оценка 3)
- [x] База данных (4 таблицы есть)
- [x] Разный функционал для авторизованных/неавторизованных
- [x] ООП
- [x] MVT архитектура
- [x] 4+ перехода (7 есть)
- [x] HTML клиент

### Этап 2: Требования для оценки 4
- [ ] Добавить пагинацию на страницу списка спортсменов
- [ ] Создать личный кабинет с редактированием профиля
- [ ] Добавить 15+ записей в каждую таблицу
- [ ] Реализовать адаптивный дизайн (CSS media queries)
- [ ] Использовать SCSS препроцессор
- [ ] Добавить формы для пользователей (кроме регистрации/авторизации)

### Этап 3: Требования для оценки 5
- [ ] Перейти на PostgreSQL
- [ ] Добавить 5+ таблиц (UserProfile, EmailVerification, UserGroup)
- [ ] Реализовать группы пользователей (минимум 2)
- [ ] Подтверждение регистрации через email с токеном
- [ ] Расширить модель пользователя (UserProfile)
- [ ] Добавить фильтрацию записей
- [ ] Добавить поиск по записям
- [ ] Реализовать кэширование
- [ ] Добавить Cookie
- [ ] Реализовать JavaScript элементы (AJAX поиск)

### Этап 4: Дополнительное задание
- [ ] Настроить Celery + Redis
- [ ] Создать асинхронные задачи (отправка email, расчёты)

---

## 💡 ДОПОЛНИТЕЛЬНЫЕ РЕКОМЕНДАЦИИ

### Улучшение UX/UI:
1. Добавить индикаторы загрузки при AJAX запросах
2. Реализовать toast уведомления об успехах/ошибках
3. Добавить графики статистики спортсмена (Chart.js)
4. Реализовать экспорт результатов в PDF/Excel

### Оптимизация:
1. Использовать `select_related` и `prefetch_related` для оптимизации запросов
2. Добавить индексы на часто используемые поля
3. Настроить логирование действий пользователей

### Безопасность:
1. Добавить rate limiting на формы входа
2. Реализовать HTTPS в production
3. Настроить Content Security Policy headers

---

## 📝 ПРИМЕРЫ КОДА ДЛЯ БЫСТРОГО СТАРТА

### 1. Быстрое добавление пагинации:

```python
# В любом view со списком объектов
from django.core.paginator import Paginator

def my_view(request):
    objects = MyModel.objects.all()
    paginator = Paginator(objects, 15)  # 15 на странице
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'template.html', {'page_obj': page_obj})
```

### 2. Декоратор для проверки прав:

```python
# laba_1/decorators.py
from django.http import HttpResponseForbidden

def coach_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        if not hasattr(request.user, 'profile') or request.user.profile.role != 'coach':
            return HttpResponseForbidden()
        return view_func(request, *args, **kwargs)
    return wrapper
```

### 3. Middleware для кастомных cookie:

```python
# CSP_1/middleware.py
class ThemeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        theme = request.COOKIES.get('theme', 'light')
        request.theme = theme
        response = self.get_response(request)
        return response
```

---

## ✅ ЧЕКЛИСТ ПЕРЕД ЗАЩИТОЙ

- [ ] Все модели созданы и миграции применены
- [ ] PostgreSQL настроен и работает
- [ ] Регистрация с подтверждением email работает
- [ ] Группы пользователей настроены
- [ ] Личный кабинет доступен и редактируется
- [ ] Поиск и фильтрация работают
- [ ] Пагинация на всех списках
- [ ] JavaScript элементы функционируют
- [ ] Адаптивный дизайн проверен на мобильных
- [ ] Минимум 15 записей в каждой таблице
- [ ] Код готов к демонстрации
- [ ] Ответы на потенциальные вопросы подготовлены

---

**Удачи в защите курсовой работы! 🎓**
