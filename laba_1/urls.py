from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.competition_registration, name='register'),

    # === ЗАДАНИЕ 8: Страница расчета очков ===
    path('', views.athlete_points_calculation, name='calculate'),

    # === НОВАЯ СТРАНИЦА: Добавление спортсмена и результата ===
    path('addmember/', views.add_member, name='add_member'),
]