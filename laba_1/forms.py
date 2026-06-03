from django import forms
from .models import Competition, Athlete, Distance, Result, UserProfile
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

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
        required=False,
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
    
class AthleteForm(forms.ModelForm):
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
            })
        }



class UserRegistrationForm(forms.ModelForm):
    """Форма регистрации пользователя"""
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        }),
        min_length=8,
        help_text='Минимум 8 символов'
    )
    
    password_confirm = forms.CharField(
        label='Подтвердить пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Повторите пароль'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Имя пользователя'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'example@mail.ru'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Иван'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Иванов'
            })
        }
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("Пользователь с таким именем уже существует")
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email уже зарегистрирован")
        return email
    
    def clean_password_confirm(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')
        
        if password and password_confirm:
            if password != password_confirm:
                raise ValidationError("Пароли не совпадают")
        return password_confirm


class UserLoginForm(forms.Form):
    """Форма входа"""
    username = forms.CharField(
        label='Имя пользователя',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите имя пользователя',
            'autofocus': True
        })
    )
    
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )
    
    remember_me = forms.BooleanField(
        label='Запомнить меня',
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )


class UserProfileForm(forms.ModelForm):
    """Форма редактирования профиля пользователя"""
    first_name = forms.CharField(
        label='Имя',
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Иван'
        })
    )
    
    last_name = forms.CharField(
        label='Фамилия',
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Иванов'
        })
    )
    
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'example@mail.ru'
        })
    )
    
    class Meta:
        model = UserProfile
        fields = ['phone', 'bio', 'avatar', 'birth_date', 'city']
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+7 (999) 999-99-99'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Расскажите о себе',
                'rows': 4
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'birth_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Москва'
            })
        }


class PasswordChangeForm(forms.Form):
    """Форма изменения пароля"""
    old_password = forms.CharField(
        label='Текущий пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите текущий пароль'
        })
    )
    
    new_password = forms.CharField(
        label='Новый пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите новый пароль'
        }),
        min_length=8
    )
    
    new_password_confirm = forms.CharField(
        label='Подтвердить новый пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Повторите новый пароль'
        })
    )
    
    def clean_new_password_confirm(self):
        new_password = self.cleaned_data.get('new_password')
        new_password_confirm = self.cleaned_data.get('new_password_confirm')
        
        if new_password and new_password_confirm:
            if new_password != new_password_confirm:
                raise ValidationError("Пароли не совпадают")
        return new_password_confirm
