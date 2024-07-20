from django.urls import path
from .views import PostCreateView, PostListView
from .views import UserPostListView, PostDetailView

urlpatterns = [
    path('create/', PostCreateView.as_view(), name='post-create'),
    path('', PostListView.as_view(), name='post-list'),
    path('main/', UserPostListView.as_view(), name='user-post-list'), # 메인페이지 (date 기준 모든 게시물 오름차순 정렬)
    path('posts/<int:post_id>/', PostDetailView.as_view(), name='post-detail'), # 페이지 1개 조회
]