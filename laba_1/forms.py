from django import forms

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
        required = True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Иванов Иван Иванович'
        })
    )
    
    email = forms.EmailField(
        label='Электронная почта',
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