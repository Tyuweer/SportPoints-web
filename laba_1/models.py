from django.db import models
from django.contrib.auth.models import User
from django.core.validators import EmailValidator
import uuid


class UserGroup(models.Model):
    GROUP_CHOICES = [
        ('viewer', 'Просмотр (неавторизованный)'),
        ('Authorized', 'Пользователь'),
        ('Coach', 'Тренер'),
        ('admin', 'Администратор'),
    ]
    
    name = models.CharField(
        "Название группы",
        max_length=50,
        choices=GROUP_CHOICES,
        unique=True
    )
    description = models.TextField(
        "Описание прав группы",
        blank=True,
        null=True
    )
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    
    class Meta:
        verbose_name = "Группа пользователей"
        verbose_name_plural = "Группы пользователей"
    
    def __str__(self):
        return self.get_name_display()


class UserProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name="Пользователь"
    )
    
    group = models.ForeignKey(
        UserGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Группа пользователя",
        related_name='users'
    )
    
    phone = models.CharField(
        "Телефон",
        max_length=20,
        blank=True,
        null=True
    )
    
    bio = models.TextField(
        "Биография",
        blank=True,
        null=True,
        max_length=500
    )
    
    avatar = models.ImageField(
        "Аватар (URL)",
        upload_to='avatars/',
        blank=True,
        null=True,
    )
    
    birth_date = models.DateField(
        "Дата рождения",
        blank=True,
        null=True
    )
    
    city = models.CharField(
        "Город",
        max_length=100,
        blank=True,
        null=True
    )
    
    email_verified = models.BooleanField(
        "Email подтвержден",
        default=False
    )
    
    created_at = models.DateTimeField("Дата создания профиля", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)
    
    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"
    
    def __str__(self):
        return f"Профиль {self.user.get_full_name() or self.user.username}"


class EmailConfirmation(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='email_confirmations',
        verbose_name="Пользователь"
    )
    
    token = models.CharField(
        "Токен подтверждения",
        max_length=100,
        unique=True,
        default=uuid.uuid4
    )
    
    email = models.EmailField(
        "Email для подтверждения",
        validators=[EmailValidator()]
    )
    
    is_confirmed = models.BooleanField(
        "Подтверждено",
        default=False
    )
    
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    confirmed_at = models.DateTimeField(
        "Дата подтверждения",
        blank=True,
        null=True
    )
    
    expires_at = models.DateTimeField(
        "Дата истечения",
        blank=True,
        null=True
    )
    
    class Meta:
        verbose_name = "Подтверждение email"
        verbose_name_plural = "Подтверждения email"
    
    def __str__(self):
        return f"Подтверждение {self.user.username} - {self.email}"


class ActivityLog(models.Model):

    ACTION_CHOICES = [
        ('login', 'Вход'),
        ('logout', 'Выход'),
        ('add_athlete', 'Добавление спортсмена'),
        ('edit_athlete', 'Редактирование спортсмена'),
        ('delete_athlete', 'Удаление спортсмена'),
        ('add_result', 'Добавление результата'),
        ('export', 'Экспорт данных'),
        ('profile_update', 'Обновление профиля'),
        ('other', 'Другое'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activities',
        verbose_name="Пользователь"
    )
    
    action = models.CharField(
        "Действие",
        max_length=50,
        choices=ACTION_CHOICES
    )
    
    description = models.TextField(
        "Описание",
        blank=True,
        null=True
    )
    
    ip_address = models.GenericIPAddressField(
        "IP адрес",
        blank=True,
        null=True
    )
    
    user_agent = models.TextField(
        "User Agent",
        blank=True,
        null=True
    )
    
    created_at = models.DateTimeField("Дата/время", auto_now_add=True)
    
    class Meta:
        verbose_name = "Журнал активности"
        verbose_name_plural = "Журналы активности"
        ordering = ['-created_at']
    
    def __str__(self):
        user_str = self.user.username if self.user else "Аноним"
        return f"{user_str} - {self.get_action_display()}"


class Competition(models.Model):

    name = models.CharField(
        "Название соревнования", 
        max_length=200,

    )
    date = models.DateField(
        "Дата проведения",

    )
    protocol_file = models.FileField(
        "Протокол PDF",
        upload_to='protocols/',
        blank=True,
        null=True,

    )
    uploaded_at = models.DateTimeField(
        "Дата загрузки",
        auto_now_add=True,

    )
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.name} ({self.date.strftime('%d.%m.%Y')})"


class Distance(models.Model):

    GENDER_CHOICES = [
        ('M', 'Мужчины'),
        ('F', 'Женщины'),
        ('X', 'Смешанная'),
    ]
    
    name = models.CharField(
        "Название дистанции",
        max_length=100,
        unique=False,

    )
    gender = models.CharField(
        "Пол",
        max_length=1,
        choices=GENDER_CHOICES,

    )
    distance_meters = models.IntegerField(
        "Дистанция (метры)",
        default=0,
        help_text="Длина дистанции в метрах"
    )
    is_relay = models.BooleanField(
        "Эстафета",
        default=False,
        help_text="Отметьте, если это эстафета"
    )
    
    class Meta:

        ordering = ['distance_meters', 'name']
        unique_together = ['name', 'gender']
    
    def __str__(self):
        gender_label = "М" if self.gender == 'M' else "Ж"
        relay_label = " (эстафета)" if self.is_relay else ""
        return f"{self.name} ({gender_label}){relay_label}"


class Athlete(models.Model):

    
    full_name = models.CharField(
        "ФИ спортсмена",
        max_length=150,
        help_text="Фамилия и имя"
    )
    birth_year = models.IntegerField(
        "Год рождения",
        null=True,
        blank=True,
    )
    team = models.CharField(
        "Команда/Регион",
        max_length=100,
        null=True,
        blank=True,
        help_text="Например: Томская область"
    )
    created_at = models.DateTimeField(
        "Дата добавления",
        auto_now_add=True,
    )
    removed = models.BooleanField(
        "Удалено",
        default=False,
        help_text="True если запись удалена"
    )
    class Meta:
        ordering = ['full_name']
        unique_together = ['full_name', 'birth_year']
    
    def __str__(self):
        year_str = self.birth_year if self.birth_year else "?"
        return f"{self.full_name} ({year_str})"


class Result(models.Model):

    
    athlete = models.ForeignKey(
        Athlete,
        on_delete=models.CASCADE,
        verbose_name="Спортсмен",
        related_name='results',
    )
    competition = models.ForeignKey(
        Competition,
        on_delete=models.CASCADE,
        verbose_name="Соревнование",
        related_name='results',
    )
    distance = models.ForeignKey(
        Distance,
        on_delete=models.CASCADE,
        verbose_name="Дистанция",
        related_name='results',
    )
    
    place = models.IntegerField(
        "Место",
        null=True,
        blank=True,

    )
    rank = models.CharField(
        "Разряд",
        max_length=100,
        null=True,
        blank=True,

    )
    result_time = models.CharField(
        "Результат",
        max_length=100,
        null=True,
        blank=True,

    )
    final_result = models.CharField(
        "Результат финала",
        max_length=100,
        null=True,
        blank=True,

    )
    best_result = models.CharField(
        "Лучший результат",
        max_length=100,
        null=True,
        blank=True,

    )
    normative = models.CharField(
        "Норматив",
        max_length=100,
        null=True,
        blank=True,

    )
    points = models.IntegerField(
    "Очки",
    default=0,
    blank=True,
    null=True,
)
    
    # # Дополнительные флаги
    # is_relay = models.BooleanField(
    #     "Эстафета",
    #     default=False,
    #     help_text="Эстафетный заплыв"
    # )
    is_manual_timing = models.BooleanField(
        "Ручной хронометраж",
        default=False,

    )
    

    parsed_at = models.DateTimeField(
        "Дата парсинга",
        auto_now_add=True,
    )
    
    class Meta:

        ordering = ['competition', 'distance', 'place']
        unique_together = ['athlete', 'competition', 'distance']
    
    def __str__(self):
        return f"{self.athlete.full_name} — {self.distance} ({self.result_time})"