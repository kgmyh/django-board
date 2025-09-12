# account/urls.py

from django.urls import path
from . import views


app_name = 'account'
urlpatterns = [
    path('join', views.join, name='join'),
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
]
