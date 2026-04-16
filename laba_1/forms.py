from django import forms
from .models import Competition, Athlete, Distance, Result

class AthleteEditForm(forms.ModelForm):
    """
    Форма редактирования спортсмена на основе модели
    """
    class Meta:
        model = Athlete
        fields = ['full_name', 'birth_year', 'team']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Иванов Иван'
            }),
            'birth_year': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '2000'
            }),
            'team': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Красноярский край'
            }),
        }

class CompetitionForm(forms.Form):


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

    athlete_name = forms.CharField(
        label="ФИО спортсмена",
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите фамилию и имя спортсмена',
            'list': 'athlete-list'
        }),
    )

    agree_pd = forms.BooleanField(
        label="Согласие на обработку персональных данных",
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )


class CompetitionSelectionForm(forms.Form):
    """
    Форма выбора соревнований
    Пользователь сам определяет что целевое, что историческое
    """
    # ОДНО целевое соревнование
    target_competition = forms.ModelChoiceField(
        label="Целевое соревнование",
        queryset=Competition.objects.all().order_by('-date'),
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        empty_label="Выберите целевое соревнование",
        help_text="Соревнования, куда отбираем спортсмена"
    )

    history_competitions = forms.ModelMultipleChoiceField(
        label="Исторические соревнования",
        queryset=Competition.objects.all().order_by('-date'),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        }),
    )





class AthleteResultForm(forms.Form):

    athlete_full_name = forms.CharField(
        label='ФИО Спортсмена',
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Иванов Иван'
        }),
        help_text="Введите Фамилию Имя"
    )

    athlete_birth_year = forms.IntegerField(
        label='Год рождения',
        required=True,
        min_value=1950,
        max_value=2025,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '2000'
        })
    )

    athlete_team = forms.CharField(
        label='Команда/Регион',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Красноярский край'
        })
    )


    competition = forms.ModelChoiceField(
        label='Соревнования',
        queryset=Competition.objects.all().order_by('-date'),
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        empty_label="Выберите соревнование"
    )

    distance = forms.ModelChoiceField(
        label='Дистанция',
        queryset=Distance.objects.all().order_by('name'),
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        empty_label="Выберите дистанцию"
    )

    result_time = forms.CharField(
        label='Время (мм:сс,мс)',
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '00:00,00'
        }),
        help_text="Формат: ММ:СС,мс"
    )


    agree_rules = forms.BooleanField(
        label='Я подтверждаю достоверность введённых данных',
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    def clean_athlete_full_name(self):
        name = self.cleaned_data.get('athlete_full_name')
        if len(name.split()) < 2:
            raise forms.ValidationError("Введите как минимум Фамилию и Имя.")
        return name

    def clean_result_time(self):

        time_str = self.cleaned_data.get('result_time')
        import re
        pattern = r'^\d{1,2}:\d{2}\,\d{1,2}$'
        if not re.match(pattern, time_str):
            raise forms.ValidationError("Время должно быть в формате ММ:СС.мс")
        return time_str