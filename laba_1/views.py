from django.shortcuts import render
from .forms import CompetitionForm, AthleteSearchForm, CompetitionSelectionForm
from .models import Athlete, Result, Competition
from django.db.models import Q

def competition_registration(request):
    form = CompetitionForm()
    submitted_data = None
    
    if request.method == 'POST':
        form = CompetitionForm(request.POST)
        if form.is_valid():
            submitted_data = {
                'full_name': form.cleaned_data['full_name'],
                'email': form.cleaned_data['email'],
                'region': form.cleaned_data['region'],
                'agree_pd': form.cleaned_data['agree_pd'],
            }

        
    
    context = {
        'form': form,
        'submitted_data': submitted_data,
    }
    
    return render(request, 'competition_registration.html', context)



# Задание 8 жестко да
def athlete_points_calculation(request):
    """
    Страница расчета очков спортсмена (Задание 8)
    Пользователь ищет спортсмена и выбирает соревнования
    """
    
    # Инициализируем формы
    search_form = AthleteSearchForm()
    selection_form = CompetitionSelectionForm()
    
    # Переменные для результатов
    athlete = None
    results = []
    total_points = 0
    error_message = None
    
    # Обработка POST запроса (отправка формы)
    if request.method == 'POST':
        search_form = AthleteSearchForm(request.POST)
        selection_form = CompetitionSelectionForm(request.POST)
        
        # Проверяем валидность ОБЕИХ форм
        if search_form.is_valid() and selection_form.is_valid():
            
            # 1. Получаем данные из форм
            athlete_name = search_form.cleaned_data['athlete_name']
            target_competition = selection_form.cleaned_data['target_competition']
            history_competitions = selection_form.cleaned_data['history_competitions']
            
            # 2. Ищем спортсмена по имени (частичное совпадение)
            athletes = Athlete.objects.filter(
                Q(full_name__icontains=athlete_name)
            ).order_by('full_name')
            
            if athletes.exists():
                # Берём первого найденного
                athlete = athletes.first()
                
                # 3. Получаем все результаты спортсмена
                all_results = Result.objects.filter(
                    athlete=athlete
                ).select_related('competition', 'distance').order_by(
                    'competition__date', 'distance__distance_meters'
                )
                
                # 4. Фильтруем по выбранным историческим соревнованиям
                if history_competitions.exists():
                    results = all_results.filter(
                        competition__in=history_competitions
                    )
                else:
                    # Если не выбраны исторические - показываем все
                    results = all_results
                
                # 5. Считаем очки (группируем по дистанциям, берём лучшие)
                best_results_by_distance = {}
                for r in results:
                    dist_name = str(r.distance)
                    if dist_name not in best_results_by_distance:
                        best_results_by_distance[dist_name] = r
                    else:
                        # Берём результат с большим количеством очков
                        if r.points > best_results_by_distance[dist_name].points:
                            best_results_by_distance[dist_name] = r
                
                # 6. Считаем общее количество очков (топ-3 дистанции)
                sorted_by_points = sorted(
                    best_results_by_distance.values(),
                    key=lambda x: float(x.points) if x.points else 0,
                    reverse=True
                )[:3]  # Берём топ-3
                
                total_points = sum(float(r.points) if r.points else 0 for r in sorted_by_points)
                
            else:
                error_message = f"Спортсмен с именем '{athlete_name}' не найден в базе"
        else:
            error_message = "Проверьте правильность заполнения формы"
    
    # Контекст для шаблона
    context = {
        'search_form': search_form,
        'selection_form': selection_form,
        'athlete': athlete,
        'results': results,
        'total_points': total_points,
        'error_message': error_message,
    }
    
    return render(request, 'athlete_points.html', context)