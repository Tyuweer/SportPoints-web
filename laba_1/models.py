from django.db import models


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
        blank=False,
        null=False,

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
        "Удален",
        default=False,
        help_text="True если объект удален (мягкое удаление)"
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
        max_length=10,
        null=True,
        blank=True,

    )
    result_time = models.CharField(
        "Результат",
        max_length=20,
        null=True,
        blank=True,

    )
    final_result = models.CharField(
        "Результат финала",
        max_length=20,
        null=True,
        blank=True,

    )
    best_result = models.CharField(
        "Лучший результат",
        max_length=20,
        null=True,
        blank=True,

    )
    normative = models.CharField(
        "Норматив",
        max_length=10,
        null=True,
        blank=True,

    )
    points = models.CharField(
        "Очки",
        default=0,

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