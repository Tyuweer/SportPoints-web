from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CompetitionForm, AthleteSearchForm, CompetitionSelectionForm, AthleteResultForm
from .models import Athlete, Result, Competition, Distance
from django.db.models import Q
from laba_1.core.utils import get_points_by_place, parse_time_to_seconds, calculate_rank_for_result


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

    search_form = AthleteSearchForm()
    selection_form = CompetitionSelectionForm()


    athlete = None
    results = []
    total_points = 0
    error_message = None
    best_results_by_distance = {}
    all_calculated_results = []
    distance_best_results = {}


    if request.method == 'POST':
        search_form = AthleteSearchForm(request.POST)
        selection_form = CompetitionSelectionForm(request.POST)

        if search_form.is_valid() and selection_form.is_valid():

        
            athlete_name = search_form.cleaned_data['athlete_name']
            target_competition = selection_form.cleaned_data['target_competition']
            history_competitions = selection_form.cleaned_data['history_competitions']

            
            athletes = Athlete.objects.filter(
                Q(full_name__icontains=athlete_name)
            ).order_by('full_name')

            if athletes.exists():
                athlete = athletes.first()

                all_results = Result.objects.filter(
                    athlete=athlete
                ).select_related('competition', 'distance').order_by(
                    'competition__date', 'distance__distance_meters'
                )


                if history_competitions.exists():
                    results = all_results.filter(competition__in=history_competitions)

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


                for dist_key in target_results_by_distance:
                    target_results_by_distance[dist_key].sort(key=lambda x: x['time'])

                all_calculated_results = []
                for r in results:
                    dist_name = str(r.distance)

                    if not r.result_time:
                        continue

                    athlete_time_sec = parse_time_to_seconds(r.result_time)
                    if athlete_time_sec is None:
                        continue

                    is_200_underwater = (
                        'Подводное плавание' in dist_name and
                        '200' in dist_name
                    )

                    predicted_place = None
                    if dist_name in target_results_by_distance:
                        target_times = target_results_by_distance[dist_name]

                        faster_count = sum(1 for t in target_times if t['time'] < athlete_time_sec)
                        predicted_place = faster_count + 1


                    if is_200_underwater:
                        calculated_points = 0
                    elif predicted_place is not None:
                        calculated_points = get_points_by_place(predicted_place)
                    else:
                        calculated_points = 0

                    calculated_rank = calculate_rank_for_result(r.distance, r.result_time)

                    all_calculated_results.append({
                        'result': r,
                        'points': calculated_points,
                        'predicted_place': predicted_place,
                        'athlete_time_sec': athlete_time_sec,
                        'calculated_rank': calculated_rank
                    })

                    if dist_name not in distance_best_results:
                        distance_best_results[dist_name] = {
                            'result': r,
                            'points': calculated_points,
                            'predicted_place': predicted_place,
                            'athlete_time_sec': athlete_time_sec
                        }
                    else:

                        if calculated_points > distance_best_results[dist_name]['points']:
                            distance_best_results[dist_name] = {
                                'result': r,
                                'points': calculated_points,
                                'predicted_place': predicted_place,
                                'athlete_time_sec': athlete_time_sec
                            }

                sorted_by_points = sorted(
                    distance_best_results.values(),
                    key=lambda x: x['points'],
                    reverse=True
                )[:3]

                total_points = sum(item['points'] for item in sorted_by_points)

                best_results_by_distance = distance_best_results
                all_calculated_results = all_calculated_results

            else:
                error_message = f"Спортсмен с именем '{athlete_name}' не найден в базе"
        else:
            error_message = "Проверьте правильность заполнения формы"

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




def add_member(request):

    form = AthleteResultForm()

    if request.method == 'POST':
        form = AthleteResultForm(request.POST)

        if form.is_valid():

            athlete = Athlete.objects.create(
                full_name=form.cleaned_data['athlete_full_name'],
                birth_year=form.cleaned_data['athlete_birth_year'],
                team=form.cleaned_data.get('athlete_team', '')
            )


            result = Result.objects.create(
                athlete=athlete,
                competition=form.cleaned_data['competition'],
                distance=form.cleaned_data['distance'],
                result_time=form.cleaned_data['result_time'],
            )


            messages.success(
                request,
                f'Спортсмен "{athlete.full_name}" успешно добавлен! '
                f'Результат: {result.result_time} ({result.points} очков)'
            )

            return redirect('add_member')

    context = {
        'form': form,
    }

    return render(request, 'add_member.html', context)