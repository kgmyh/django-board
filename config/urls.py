"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path("", TemplateView.as_view(template_name='home.html'), name='home'),
    path('admin/', admin.site.urls),
    path('board/', include('board.urls')),
    path('account/', include('account.urls')),
]

############################################################
# 업로드된 파일을 client가 요청할 수 있도록 처리.
############################################################
from django.conf.urls.static import static 
from . import settings   #config/settings.py 임포트
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  
#UPLOAD된 파일들을 STATIC 파일로 서비스하기 위한 설정(url 시작 path, media 파일의 root 디렉토리.)