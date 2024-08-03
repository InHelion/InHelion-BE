from django.urls import path
from .views import PostCreateView, CommentCreateView, CommentListView, CommentDeleteView
from .views import UserPostListView, PostDetailView, PostDeleteView, MissEmailNotificationView

urlpatterns = [
    path('create/', PostCreateView.as_view(), name='post-create'), # 게시물 생성
    path('posts/<int:post_id>/delete/', PostDeleteView.as_view(), name='post-delete'), # 게시물 삭제
    path('main/', UserPostListView.as_view(), name='user-post-list'), # 메인페이지 (date 기준 모든 게시물 오름차순 정렬) + 평균달성률
    path('posts/<int:post_id>/', PostDetailView.as_view(), name='post-detail'), # 페이지 1개 조회
    path('posts/<int:post_id>/comments/', CommentListView.as_view(), name='comment-list'), # 페이지 1개의 모든 댓글 조회
    path('posts/<int:post_id>/comments/create/', CommentCreateView.as_view(), name='comment-create'), # 댓글 생성
    path('posts/<int:post_id>/comments/<int:pk>/delete/', CommentDeleteView.as_view(), name='comment-delete'), # 댓글 삭제
    path('miss_email/', MissEmailNotificationView.as_view(), name='miss_email_notification') # 보고싶어 이메일

    #path('', PostListView.as_view(), name='post-list'),
    #path('<int:pk>/comments/update/', CommentUpdateView.as_view(), name='comment-update'), # 댓글 수정
]
