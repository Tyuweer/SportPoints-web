from django.contrib import admin
from .models import (
    Competition, Distance, Athlete, Result, 
    UserGroup, UserProfile, EmailConfirmation, ActivityLog
)


@admin.register(UserGroup)
class UserGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'group', 'email_verified', 'city', 'created_at')
    list_filter = ('group', 'email_verified', 'created_at')
    search_fields = ('user__username', 'user__email', 'city')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(EmailConfirmation)
class EmailConfirmationAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'is_confirmed', 'created_at')
    list_filter = ('is_confirmed', 'created_at')
    search_fields = ('user__username', 'email')
    readonly_fields = ('token', 'created_at', 'confirmed_at')


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'created_at', 'ip_address')
    list_filter = ('action', 'created_at')
    search_fields = ('user__username', 'description')
    readonly_fields = ('created_at',)
    list_per_page = 50


@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'date', 'uploaded_at', 'protocol_file')
    list_filter = ('date',)
    search_fields = ('id', 'name')
    ordering = ('-date',)
    readonly_fields = ('uploaded_at',)


@admin.register(Distance)
class DistanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'gender', 'distance_meters', 'is_relay')
    list_filter = ('gender', 'is_relay')
    search_fields = ('id', 'name')
    ordering = ('distance_meters', 'name')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Athlete)
class AthleteAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'birth_year', 'team', 'removed', 'created_at')
    list_filter = ('team', 'birth_year', 'removed')
    search_fields = ('id', 'full_name', 'team')
    ordering = ('full_name',)


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'athlete', 'competition', 'distance', 'place', 'result_time', 'points')
    list_filter = ('competition', 'distance', 'rank')
    search_fields = ('id', 'athlete__full_name', 'distance__name', 'competition__name')
    ordering = ('competition', 'distance', 'place')
    list_per_page = 100