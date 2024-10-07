
from django.shortcuts import render
from .models import Problem

def problem_list(request):
    if request.user.userprofile.is_supervisor:
        problems = Problem.objects.all()
    else:
        problems = Problem.objects.filter(club=request.user.userprofile.club)
    return render(request, 'problems_list.html', {'problems': problems})
