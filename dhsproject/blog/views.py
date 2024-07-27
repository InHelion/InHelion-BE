from rest_framework import generics, permissions, status
from .models import Post, Comment
from users.models import CustomUser
from django.contrib.auth.models import User
from .serializers import PostCreateSerializer, PostDetailSerializer, PostListSerializer,CommentSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, redirect
from django.core.mail import send_mail
from django.http import HttpResponse
from datetime import datetime, timedelta
from rest_framework.exceptions import PermissionDenied

class PostCreateView(generics.CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # 현재 사용자의 정보를 저장합니다.
        post = serializer.save(
            user=self.request.user,
            user_meals=self.request.user.meals,
            user_exercises=self.request.user.exercises,
            user_medications=self.request.user.medications,
            user_sleep=self.request.user.sleep
        )
        post.achievement_rate_value = post.achievement_rate()
        post.save()

class PostListView(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Post.objects.filter(user=self.request.user).order_by('-date')

class CommentCreateView(generics.CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_id')
        post = Post.objects.get(id=post_id)
        comment = serializer.save(user=self.request.user, post=post)
        if comment.protector:
            comment.content = f" [보호자] | {comment.content}"
        comment.save()


###한페이지뷰(특정 한페이지의 모든 댓글 조회(생성시간 기준 정렬))
class CommentListView(generics.ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        post_id = self.kwargs['post_id']
        post = get_object_or_404(Post, id=post_id, user=self.request.user)
        return Comment.objects.filter(post=post).order_by('created_at')

class CommentUpdateView(generics.UpdateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_object(self):
        comment = super().get_object()
        if comment.user != self.request.user:
            raise PermissionDenied("수정 권한이 없습니다.")
        return comment
    
class CommentDeleteView(generics.DestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        comment = super().get_object()
        if comment.user != self.request.user:
            raise PermissionDenied("삭제 권한이 없습니다.")
        return comment
    
    def delete(self, request, *args, **kwargs):
        comment = self.get_object()
        self.perform_destroy(comment)
        return Response({"message": "삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)
    
### 메인페이지(date기준 오름차순 사용자의 모든 게시물 조회) + 최근 10개의 게시물 기준 평균 달성률 추가
class UserPostListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # 게시물을 날짜 기준 오름차순으로 정렬
        posts = Post.objects.filter(user=request.user).order_by('date')
        serializer = PostListSerializer(posts, many=True)

        # 최근 10개의 게시물 기준 평균 달성률 계산
        recent_posts = posts[::-1][:10]  # 최근 10개의 게시물을 가져옴 (오름차순 정렬 후 슬라이싱)

        total_achievement_rate = 0
        for post in recent_posts:
            achievement_rate = post.achievement_rate()
            total_achievement_rate += achievement_rate

        count = len(recent_posts)
        average_achievement_rate = round(total_achievement_rate / count, 2) if count > 0 else 0

        return Response({
            'posts': serializer.data,
            'TenDaysAverage': average_achievement_rate
        }, status=status.HTTP_200_OK)

### 보고싶어 이메일 발송
class MissEmailNotificationView(APIView):
    def get(self, request, user_id):
        user_profile = get_object_or_404(CustomUser, id=user_id)
        
        user_name = user_profile.username  

        email_subject = '< 다했슈로부터 보고싶어 알림이 도착했습니다! >'
        email_message = f'{user_name}님께서 보호자분의 연락을 기다리고 있습니다.\n빠른 연락을 부탁드립니다 :) \n\nfrom 다했슈'
        from_email = 'kmy737785@gmail.com' #발송할 비즈니스 이메일로 변경해야함
        
        recipient_list = [user_profile.email]

        send_mail(
            email_subject,
            email_message,
            from_email,
            recipient_list,
            fail_silently=False,
        )
        return Response({'message': '보고싶어 알림이 성공적으로 전송되었습니다.'})

###한페이지뷰(사용자의 특정 한 페이지 조회 (게시물 id 이용))
class PostDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id, user=request.user)
        serializer = PostDetailSerializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)

###게시물삭제
class PostDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, post_id):
        post = get_object_or_404(Post, id=post_id, user=request.user)
        post.delete()
        return Response({"message": "게시물이 성공적으로 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)
