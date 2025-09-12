from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse

from .forms import CustomUserCreationForm


@require_http_methods(["GET", "POST"])
def join(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'account/join_form.html', {'form': form})


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'account/login_form.html', {'form': form})


@login_required
@require_http_methods(["POST"])
def logout_view(request):
    auth_logout(request)
    return redirect('home')

    
