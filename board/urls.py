# board/urls.py
from django.urls import path
from django.views.generic import TemplateView

from board import views

app_name = 'board'
urlpatterns = [
    path('detail/<int:pk>',views.PostDetailView.as_view(), name='detail'), #게시물 상세페이지
    path('create', views.PostCreateView.as_view(), name='create'), #글 등록 View url
    path('update/<int:pk>', views.PostUpdateView.as_view(), name='update'), #글 수정 url. GET: 수정할 게시물의 pk을 path parameter 받아야함.
    path('delete/<int:pk>', views.post_delete, name='delete'), #삭제처리.
    path('list', views.PostListView.as_view(), name='list'), #글 목록 조회.
] 

