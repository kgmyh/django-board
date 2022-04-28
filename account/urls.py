# account/urls.py

from django.urls import path
from . import views
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import AuthenticationForm
from . import forms


app_name = 'account'
urlpatterns = [
    # path('join', views.UserCreateView.as_view(), name='join'), #가입
    path('join', CreateView.as_view(template_name='account/join_form.html', 
                                    form_class=forms.CustomUserCreationForm,
                                    success_url='/'), name='join'),
    # path('login', views.UserLoginView.as_view(), name='login'), #로그인 
    path('login', LoginView.as_view(template_name='account/login_form.html', form_class=AuthenticationForm), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),

]