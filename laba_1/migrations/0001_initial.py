

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Competition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Название соревнования')),
                ('date', models.DateField(verbose_name='Дата проведения')),
                ('protocol_file', models.FileField(blank=True, null=True, upload_to='protocols/', verbose_name='Протокол PDF')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата загрузки')),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='Athlete',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(help_text='Фамилия и имя', max_length=150, verbose_name='ФИ спортсмена')),
                ('birth_year', models.IntegerField(blank=True, null=True, verbose_name='Год рождения')),
                ('team', models.CharField(blank=True, help_text='Например: Томская область', max_length=100, null=True, verbose_name='Команда/Регион')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')),
            ],
            options={
                'ordering': ['full_name'],
                'unique_together': {('full_name', 'birth_year')},
            },
        ),
        migrations.CreateModel(
            name='Distance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Название дистанции')),
                ('gender', models.CharField(choices=[('M', 'Мужчины'), ('F', 'Женщины'), ('X', 'Смешанная')], max_length=1, verbose_name='Пол')),
                ('distance_meters', models.IntegerField(default=0, help_text='Длина дистанции в метрах', verbose_name='Дистанция (метры)')),
                ('is_relay', models.BooleanField(default=False, help_text='Отметьте, если это эстафета', verbose_name='Эстафета')),
            ],
            options={
                'ordering': ['distance_meters', 'name'],
                'unique_together': {('name', 'gender')},
            },
        ),
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('place', models.IntegerField(blank=True, null=True, verbose_name='Место')),
                ('rank', models.CharField(blank=True, max_length=10, null=True, verbose_name='Разряд')),
                ('result_time', models.CharField(blank=True, max_length=20, null=True, verbose_name='Результат')),
                ('final_result', models.CharField(blank=True, max_length=20, null=True, verbose_name='Результат финала')),
                ('best_result', models.CharField(blank=True, max_length=20, null=True, verbose_name='Лучший результат')),
                ('normative', models.CharField(blank=True, max_length=10, null=True, verbose_name='Норматив')),
                ('points', models.CharField(default=0, verbose_name='Очки')),
                ('is_manual_timing', models.BooleanField(default=False, verbose_name='Ручной хронометраж')),
                ('parsed_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата парсинга')),
                ('athlete', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='results', to='laba_1.athlete', verbose_name='Спортсмен')),
                ('competition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='results', to='laba_1.competition', verbose_name='Соревнование')),
                ('distance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='results', to='laba_1.distance', verbose_name='Дистанция')),
            ],
            options={
                'ordering': ['competition', 'distance', 'place'],
                'unique_together': {('athlete', 'competition', 'distance')},
            },
        ),
    ]
