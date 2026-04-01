from django.urls import path
from . import views

urlpatterns = [
    path('', views.competition_registration, name='competition_registration'),
]