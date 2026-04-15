from django.contrib import admin
from .models import Competition, Distance, Athlete, Result


@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    """
    Админка для соревнований
    Админ загружает PDF протоколы здесь
    """
    list_display = ('id','name', 'date', 'uploaded_at', 'protocol_file')
    list_filter = ('date',)
    search_fields = ('name',)
    ordering = ('-date',)
    readonly_fields = ('uploaded_at',)  # Поле только для просмотра


@admin.register(Distance)
class DistanceAdmin(admin.ModelAdmin):
    """
    Админка для дистанций
    """
    list_display = ('id', 'name', 'gender', 'distance_meters', 'is_relay')
    list_filter = ('gender', 'is_relay')
    search_fields = ('name',)
    ordering = ('distance_meters', 'name')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Athlete)
class AthleteAdmin(admin.ModelAdmin):
    """
    Админка для спортсменов
    """
    list_display = ('id', 'full_name', 'birth_year', 'team', 'created_at')
    list_filter = ('team', 'birth_year')
    search_fields = ('full_name', 'team')
    ordering = ('full_name',)


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    """
    Админка для результатов
    """
    list_display = ('id', 'athlete', 'competition', 'distance', 'place', 'result_time', 'points')
    list_filter = ('competition', 'distance', 'rank')
    list_filter = ('competition', 'distance', 'rank')
    search_fields = ('athlete__full_name', 'distance__name')
    ordering = ('competition', 'distance', 'place')
    list_per_page = 50
    
    # # Запрет редактирования результатов (они из протокола)
    # def has_change_permission(self, request, obj=None):
    #     return False  # Только просмотр
    
    # def has_delete_permission(self, request, obj=None):
    #     return False  # Нельзя удалять