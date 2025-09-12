# account/views.py
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.views.decorators.http import require_GET

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


# 비권장: GET 요청으로 로그아웃 처리 (디자인 요구사항 대응)
@require_GET
def logout_get(request):
    logout(request)
    return redirect('home')
