# board/urls.py
from django.urls import path
from django.views.generic import TemplateView

from board import views

app_name = 'board'
urlpatterns = [
    path('detail/<int:pk>',views.post_detail, name='detail'), #게시물 상세페이지
    path('create', views.post_create, name='create'), #글 등록 View url
    path('update/<int:pk>', views.post_update, name='update'), #글 수정 url. GET: 수정할 게시물의 pk을 path parameter 받아야함.
    path('delete/<int:pk>', views.post_delete, name='delete'), #삭제처리.
    path('list', views.post_list, name='list'), #글 목록 조회.
    # 댓글
    path('post/<int:post_pk>/comments/create', views.comment_create, name='comment_create'),
    path('comments/<int:pk>/update', views.comment_update, name='comment_update'),
    path('comments/<int:pk>/delete', views.comment_delete, name='comment_delete'),
] 
