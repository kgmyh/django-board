from django.urls import path

from board import views_cbv as views
from board import views as fbv

app_name = 'board'
urlpatterns = [
    # CBV routes backup
    path('detail/<int:pk>', views.PostDetailView.as_view(), name='detail'),
    path('create', views.PostCreateView.as_view(), name='create'),
    path('update/<int:pk>', views.PostUpdateView.as_view(), name='update'),
    # delete was FBV originally
    path('delete/<int:pk>', fbv.post_delete, name='delete'),
    path('list', views.PostListView.as_view(), name='list'),
    # comments are FBV endpoints
    path('post/<int:post_pk>/comments/create', fbv.comment_create, name='comment_create'),
    path('comments/<int:pk>/update', fbv.comment_update, name='comment_update'),
    path('comments/<int:pk>/delete', fbv.comment_delete, name='comment_delete'),
]

