from django import forms
from .models import Competition, Athlete

class CompetitionForm(forms.Form):
    """
    Форма регистрации участника на соревнования (Задание 7)
    Эта форма продолжает работать для старого функционала
    """
    
    REGION_CHOICES = [
        ('', 'Выберите регион'),
        ('Moscow', 'Москва'),
        ('Spb', 'Санкт-Петербург'),
        ('Kazan', 'Казань'),
        ('Nsk', 'Новосибирск'),
        ('Ekat', 'Екатеринбург'),
        ('Kras', 'Красноярск'),
    ]
    
    full_name = forms.CharField(
        label='ФИО участника',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Иванов Иван Иванович'
        })
    )
    
    email = forms.EmailField(
        label='Электронная почта',
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'example@mail.ru'
        })
    )
    
    region = forms.ChoiceField(
        label='Регион',
        choices=REGION_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    agree_pd = forms.BooleanField(
        label='Согласие на обработку персональных данных',
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
        })
    )


class AthleteSearchForm(forms.Form):
    """
    Форма поиска спортсмена
    Служебное поле - не сохраняется в БД
    """
    athlete_name = forms.CharField(
        label="ФИО спортсмена",
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите фамилию спортсмена',
            'list': 'athlete-list'  # Для автокомплита
        }),
        help_text="Начните вводить фамилию для поиска"
    )
    
    # Служебное поле - согласие (не хранится в БД)
    agree_pd = forms.BooleanField(
        label="Согласие на обработку персональных данных",
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Можно добавить подсказки с существующими спортсменами
        # для автокомплита в шаблоне


class CompetitionSelectionForm(forms.Form):
    """
    Форма выбора соревнований
    Пользователь сам определяет что целевое, что историческое
    """
    # ОДНО целевое соревнование
    target_competition = forms.ModelChoiceField(
        label="🎯 Целевое соревнование",
        queryset=Competition.objects.all().order_by('-date'),
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        empty_label="Выберите целевое соревнование",
        help_text="Соревнования, куда отбираем спортсмена"
    )
    
    # НЕСКОЛЬКО исторических соревнований
    history_competitions = forms.ModelMultipleChoiceField(
        label="📋 Исторические соревнования",
        queryset=Competition.objects.all().order_by('-date'),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        }),
        help_text="Выберите соревнования, откуда брать результаты (можно несколько)"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Исключаем целевое из исторических (визуально разделим в шаблоне)