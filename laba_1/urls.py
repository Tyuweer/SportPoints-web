from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.competition_registration, name='register'),

    path('calc', views.athlete_points_calculation, name='calculate'),

    path('addmember/', views.add_member, name='add_member'),
    # Задание 9 - многостраничное приложение
    path('', views.athlete_list, name='athlete_list'),
    path('athletes/<int:pk>/', views.athlete_detail, name='athlete_detail'),
    path('athletes/<int:pk>/edit/', views.athlete_edit, name='athlete_edit'),
    path('athletes/<int:pk>/delete/', views.athlete_delete, name='athlete_delete'),
]