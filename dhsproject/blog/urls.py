from django.urls import path
from .views import PostCreateView, PostListView, CommentCreateView, CommentListView

urlpatterns = [
    path('create/', PostCreateView.as_view(), name='post-create'),
    path('', PostListView.as_view(), name='post-list'),
    path('<int:post_id>/comments/', CommentListView.as_view(), name='comment-list'),
    path('<int:post_id>/comments/create/', CommentCreateView.as_view(), name='comment-create'),
]