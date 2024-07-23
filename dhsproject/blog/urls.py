from django.urls import path
from .views import PostCreateView, PostListView, CommentCreateView, CommentListView
from .views import UserPostListView, PostDetailView, PostDeleteView

urlpatterns = [
    path('create/', PostCreateView.as_view(), name='post-create'),
    path('', PostListView.as_view(), name='post-list'),
    path('posts/<int:post_id>/delete/', PostDeleteView.as_view(), name='post-delete'), # 게시물 삭제
    path('main/', UserPostListView.as_view(), name='user-post-list'), # 메인페이지 (date 기준 모든 게시물 오름차순 정렬)
    path('posts/<int:post_id>/', PostDetailView.as_view(), name='post-detail'), # 페이지 1개 조회
    path('<int:post_id>/comments/', CommentListView.as_view(), name='comment-list'), # 페이지 1개의 모든 댓글 조회
    path('<int:post_id>/comments/create/', CommentCreateView.as_view(), name='comment-create'),
]