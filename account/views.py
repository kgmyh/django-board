# account/views.py
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm

from .forms import CustomUserCreationForm
# 가입 View
class UserCreateView(CreateView):
    template_name = "account/join_form.html"
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('home')

# 로그인 처리 View
class UserLoginView(LoginView):
    template_name = 'account/login_form.html'
    form_class = AuthenticationForm