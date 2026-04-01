from django.shortcuts import render
from .forms import CompetitionForm

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