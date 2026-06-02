from django.urls import path
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('confirm-email/<str:token>/', views.confirm_email, name='confirm_email'),
    
    # Profile
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/password/', views.password_change, name='password_change'),
    path('profile/activity/', views.activity_log_view, name='activity_log'),
    
    # Competitions
    path('competitions/', views.competition_list, name='competition_list'),
    path('register-competition/', views.competition_registration, name='register_competition'),
    path('calc', views.athlete_points_calculation, name='calculate'),
    path('addmember/', views.add_member, name='add_member'),
    
    # Athletes
    path('', views.athlete_list, name='athlete_list'),
    path('athletes/<int:pk>/', views.athlete_detail, name='athlete_detail'),
    path('athletes/<int:pk>/edit/', views.athlete_edit, name='athlete_edit'),
    path('athletes/<int:pk>/delete/', views.athlete_delete, name='athlete_delete'),
    
    # AJAX endpoints
    path('export-excel/', views.export_excel_ajax, name='export_excel_ajax'),
    path('athletes/delete-ajax/<int:pk>/', views.athlete_delete_ajax, name='athlete_delete_ajax'),
]