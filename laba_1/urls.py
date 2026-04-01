from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.competition_registration, name='register'),
    
    # === ЗАДАНИЕ 8: Новая страница расчета очков ===
    path('', views.athlete_points_calculation, name='calculate'),
]