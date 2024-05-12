import uuid
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import SignupForm, ProfileForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def signup(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if not form.data.get("username"):
            form.data = form.data.copy()
            form.data["username"] = str(uuid.uuid4())
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = SignupForm()
    return render(request, 'user/signup.html', {'form': form})


@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = ProfileForm(instance=request.user, data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile was updated successfully")
            return render(request, 'user/profile_edit.html', {'form': form})
        else:
            messages.warning(request, "Please fix the errors below")
            return render(request, 'user/profile_edit.html', {'form': form})
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'user/profile_edit.html', {'form': form})
