from django.shortcuts import render
from .forms import CompetitionForm, AthleteSearchForm, CompetitionSelectionForm
from .models import Athlete, Result, Competition, Distance
from django.db.models import Q
from laba_1.core.utils import get_points_by_place, parse_time_to_seconds


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

    Логика расчета:
    1. Берем время спортсмена из исторических соревнований
    2. Подставляем это время в целевое соревнование
    3. Определяем какое место было бы с этим временем
    4. Рассчитываем очки по этому месту
    5. Для 200м подводное плавание очки всегда = 0
    """

    # Инициализируем формы
    search_form = AthleteSearchForm()
    selection_form = CompetitionSelectionForm()

    # Переменные для результатов
    athlete = None
    results = []
    total_points = 0
    error_message = None
    best_results_by_distance = {}
    all_calculated_results = []
    distance_best_results = {}

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

                # 3. Получаем все результаты спортсмена в исторических соревнованиях
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

                # 5. Получаем все результаты целевого соревнования для сравнения
                target_results_by_distance = {}
                for r in Result.objects.filter(
                    competition=target_competition
                ).select_related('distance').filter(
                    result_time__isnull=False
                ):
                    dist_key = str(r.distance)
                    if dist_key not in target_results_by_distance:
                        target_results_by_distance[dist_key] = []
                    time_sec = parse_time_to_seconds(r.result_time)
                    if time_sec is not None:
                        target_results_by_distance[dist_key].append({
                            'time': time_sec,
                            'place': r.place,
                            'athlete': r.athlete.full_name
                        })

                # Сортируем результаты целевого соревнования по времени (лучшее первое)
                for dist_key in target_results_by_distance:
                    target_results_by_distance[dist_key].sort(key=lambda x: x['time'])

                # 6. Для каждого результата спортсмена считаем predicted place и очки
                all_calculated_results = []  # Все результаты с расчетными очками

                for r in results:
                    dist_name = str(r.distance)

                    # Пропускаем если нет времени
                    if not r.result_time:
                        continue

                    athlete_time_sec = parse_time_to_seconds(r.result_time)
                    if athlete_time_sec is None:
                        continue

                    # Проверяем, является ли дистанция "200м подводное плавание"
                    is_200_underwater = (
                        'Подводное плавание' in dist_name and
                        '200' in dist_name
                    )

                    # Рассчитываем место в целевом соревновании
                    predicted_place = None
                    if dist_name in target_results_by_distance:
                        target_times = target_results_by_distance[dist_name]
                        # Считаем сколько людей проплыли быстрее
                        faster_count = sum(1 for t in target_times if t['time'] < athlete_time_sec)
                        predicted_place = faster_count + 1

                    # Рассчитываем очки
                    if is_200_underwater:
                        # Для 200м подводное плавание очки всегда 0
                        calculated_points = 0
                    elif predicted_place is not None:
                        calculated_points = get_points_by_place(predicted_place)
                    else:
                        calculated_points = 0

                    # Добавляем результат в список всех рассчитанных результатов
                    all_calculated_results.append({
                        'result': r,
                        'points': calculated_points,
                        'predicted_place': predicted_place,
                        'athlete_time_sec': athlete_time_sec
                    })

                    # Сохраняем лучший результат по дистанции для подсчета топ-3
                    if dist_name not in distance_best_results:
                        distance_best_results[dist_name] = {
                            'result': r,
                            'points': calculated_points,
                            'predicted_place': predicted_place,
                            'athlete_time_sec': athlete_time_sec
                        }
                    else:
                        # Берём результат с большим количеством очков
                        if calculated_points > distance_best_results[dist_name]['points']:
                            distance_best_results[dist_name] = {
                                'result': r,
                                'points': calculated_points,
                                'predicted_place': predicted_place,
                                'athlete_time_sec': athlete_time_sec
                            }

                # 7. Считаем общее количество очков (топ-3 дистанции)
                sorted_by_points = sorted(
                    distance_best_results.values(),
                    key=lambda x: x['points'],
                    reverse=True
                )[:3]  # Берём топ-3

                total_points = sum(item['points'] for item in sorted_by_points)

                best_results_by_distance = distance_best_results
                all_calculated_results = all_calculated_results

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
        'best_results_by_distance': best_results_by_distance,
        'all_calculated_results': all_calculated_results,
    }

    return render(request, 'athlete_points.html', context)