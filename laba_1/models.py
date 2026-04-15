from django.db import models


class Competition(models.Model):
    """
    Таблица 1: Соревнования
    Все соревнования хранятся одинаково.
    """
    
    name = models.CharField(
        "Название соревнования", 
        max_length=200,
        help_text="Например: Чемпионат России 2025"
    )
    date = models.DateField(
        "Дата проведения",
        help_text="Когда состоялись соревнования"
    )
    protocol_file = models.FileField(
        "Протокол PDF",
        upload_to='protocols/',
        blank=True,
        null=True,
        help_text="Загрузите PDF файл с протоколом"
    )
    uploaded_at = models.DateTimeField(
        "Дата загрузки",
        auto_now_add=True,
        help_text="Автоматически заполняется при загрузке"
    )
    
    class Meta:
        verbose_name = "Соревнование"
        verbose_name_plural = "Соревнования"
        ordering = ['-date']  # Сортировка: новые сверху
    
    def __str__(self):
        return f"{self.name} ({self.date.strftime('%d.%m.%Y')})"


class Distance(models.Model):
    """
    Таблица 2: Дистанции (справочник)
    """
    
    GENDER_CHOICES = [
        ('M', 'Мужчины'),
        ('F', 'Женщины'),
        ('X', 'Смешанная'),
    ]
    
    name = models.CharField(
        "Название дистанции",
        max_length=100,
        unique=False,
        help_text="Например: Плавание в ластах - 100 м"
    )
    gender = models.CharField(
        "Пол",
        max_length=1,
        choices=GENDER_CHOICES,
        help_text="Мужчины или Женщины"
    )
    distance_meters = models.IntegerField(
        "Дистанция (метры)",
        default=0,
        help_text="Длина дистанции в метрах (50, 100, 200...)"
    )
    is_relay = models.BooleanField(
        "Эстафета",
        default=False,
        help_text="Отметьте, если это эстафета"
    )
    
    class Meta:
        verbose_name = "Дистанция"
        verbose_name_plural = "Дистанции"
        ordering = ['distance_meters', 'name']
        unique_together = ['name', 'gender']
    
    def __str__(self):
        gender_label = "М" if self.gender == 'M' else "Ж"
        relay_label = " (эстафета)" if self.is_relay else ""
        return f"{self.name} ({gender_label}){relay_label}"


class Athlete(models.Model):
    """
    Таблица 3: Спортсмены
    """
    
    full_name = models.CharField(
        "ФИО спортсмена",
        max_length=150,
        help_text="Фамилия Имя Отчество"
    )
    birth_year = models.IntegerField(
        "Год рождения",
        null=True,
        blank=True,
        help_text="Например: 2005"
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
        help_text="Когда спортсмен впервые появился в базе"
    )
    removed = models.BooleanField(
        "Удален",
        default=False,
        help_text="Отметьте True для мягкого удаления объекта"
    )
    
    class Meta:
        verbose_name = "Спортсмен"
        verbose_name_plural = "Спортсмены"
        ordering = ['full_name']
        unique_together = ['full_name', 'birth_year']
    
    def __str__(self):
        year_str = self.birth_year if self.birth_year else "?"
        return f"{self.full_name} ({year_str})"


class Result(models.Model):
    """
    Таблица 4: Результаты выступлений
    """
    
    athlete = models.ForeignKey(
        Athlete,
        on_delete=models.CASCADE,
        verbose_name="Спортсмен",
        related_name='results',
        help_text="Кто показал результат"
    )
    competition = models.ForeignKey(
        Competition,
        on_delete=models.CASCADE,
        verbose_name="Соревнование",
        related_name='results',
        help_text="На каких соревнованиях"
    )
    distance = models.ForeignKey(
        Distance,
        on_delete=models.CASCADE,
        verbose_name="Дистанция",
        related_name='results',
        help_text="Какая дистанция"
    )
    
    # Данные из протокола
    place = models.IntegerField(
        "Место",
        null=True,
        blank=True,
        help_text="Занятое место (1, 2, 3...)"
    )
    rank = models.CharField(
        "Разряд",
        max_length=10,
        null=True,
        blank=True,
        help_text="МС, КМС, ЗМС и т.д."
    )
    result_time = models.CharField(
        "Результат",
        max_length=20,
        null=True,
        blank=True,
        help_text="Время: 00:16,46"
    )
    final_result = models.CharField(
        "Результат финала",
        max_length=20,
        null=True,
        blank=True,
        help_text="Если был финал"
    )
    best_result = models.CharField(
        "Лучший результат",
        max_length=20,
        null=True,
        blank=True,
        help_text="Лучший из заплывов"
    )
    normative = models.CharField(
        "Норматив",
        max_length=10,
        null=True,
        blank=True,
        help_text="На какой норматив проплыл"
    )
    points = models.CharField(
        "Очки",
        default=0,
        help_text="Количество очков за этот результат"
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
        help_text="Ручное время (не автоматическое)"
    )
    
    # Автоматическая дата парсинга
    parsed_at = models.DateTimeField(
        "Дата парсинга",
        auto_now_add=True,
        help_text="Когда результат добавлен в базу"
    )
    
    class Meta:
        verbose_name = "Результат"
        verbose_name_plural = "Результаты"
        ordering = ['competition', 'distance', 'place']
        unique_together = ['athlete', 'competition', 'distance']
    
    def __str__(self):
        return f"{self.athlete.full_name} — {self.distance} ({self.result_time})"