from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.competition_registration, name='register'),

    # === ЗАДАНИЕ 8: Страница расчета очков ===
    path('', views.athlete_points_calculation, name='calculate'),

    # === НОВАЯ СТРАНИЦА: Добавление спортсмена и результата ===
    path('addmember/', views.add_member, name='add_member'),
    
    # === НОВЫЕ МАРШРУТЫ ДЛЯ СПИСКА, ДЕТАЛИЗАЦИИ, РЕДАКТИРОВАНИЯ И УДАЛЕНИЯ ===
    path('athletes/', views.athlete_list, name='athlete_list'),
    path('athlete/<int:athlete_id>/', views.athlete_detail, name='athlete_detail'),
    path('athlete/<int:athlete_id>/edit/', views.athlete_edit, name='athlete_edit'),
    path('athlete/<int:athlete_id>/remove/', views.athlete_remove, name='athlete_remove'),
]