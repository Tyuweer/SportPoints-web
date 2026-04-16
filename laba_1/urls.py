from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.competition_registration, name='register'),

    path('', views.athlete_points_calculation, name='calculate'),

    path('addmember/', views.add_member, name='add_member'),
]