from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import SignupForm


def signup(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = SignupForm()
    return render(request, 'user/signup.html', {'form': form})

