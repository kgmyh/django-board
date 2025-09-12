from django.urls import path
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import AuthenticationForm

from . import forms


app_name = 'account'
urlpatterns = [
    # CBV routes backup
    path('join', CreateView.as_view(template_name='account/join_form.html',
                                    form_class=forms.CustomUserCreationForm,
                                    success_url='/'), name='join'),
    path('login', LoginView.as_view(template_name='account/login_form.html', form_class=AuthenticationForm), name='login'),
    path('logout', LogoutView.as_view(next_page=reverse_lazy('home')), name='logout'),
]

