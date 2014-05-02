from django.shortcuts import render, redirect

def index(request):
    if request.user.is_authenticated():
        return redirect('home')
    context = {}
    return render(request, 'maestor/index.html', context)

def home(request):
    context = {}
    return render(request, 'maestor/home.html', context)