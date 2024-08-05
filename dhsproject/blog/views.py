from rest_framework import generics, permissions, status
from .models import Post, Comment
from users.models import CustomUser
from django.contrib.auth.models import User
from .serializers import PostCreateSerializer, PostDetailSerializer, PostListSerializer,CommentSerializer
from users.serializers import UserSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from django.shortcuts import get_object_or_404, redirect
from django.core.mail import send_mail
from django.http import HttpResponse
from datetime import datetime, timedelta
from rest_framework.exceptions import PermissionDenied
from django.conf import settings
from django.core.mail import EmailMessage
import smtplib
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

#####게시물 생성#####
class PostCreateView(generics.CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="사용자 게시물 생성 API 입니다.\n생성시 달성률이 100%가 아니라면 사용자 정보에 등록된 이메일로 메일이 전송됩니다.",
        operation_summary="게시물 생성",
        request_body=PostCreateSerializer,
        responses={201: PostCreateSerializer, 400: "Bad Request"}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user

        post = Post(
            user=user,
            date=serializer.validated_data.get('date'),
            medication_today=serializer.validated_data.get('medication_today'),
            exercise_time=serializer.validated_data.get('exercise_time'),
            meal_count=serializer.validated_data.get('meal_count'),
            sleep_time=serializer.validated_data.get('sleep_time'),
            daily_summary=serializer.validated_data.get('daily_summary'),
            user_meals=user.meals,
            user_exercises=user.exercises,
            user_medications=user.medications,
            user_sleep=user.sleep
        )
        
        post.achievement_rate_value = post.achievement_rate()
        post.save()

        # 달성률이 100%가 되지 않으면 이메일을 보냄
        if post.achievement_rate_value != 100:
            self.send_achievement_email(user, post)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def send_achievement_email(self, user, post):
        subject = f"(다햇슈 알림) {user.username}님의 달성률이 100% 미만입니다."
        message = (
            f"{user.username}님의 {post.date.strftime('%Y-%m-%d')}일자 달성률이 100%를 만족하지 못했습니다.\n\n"
            "보호자님의 확인을 부탁드립니다 :)\n\n"
            "from 다햇슈"
        )
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user.email]

        # 이메일을 생성하고 인코딩을 설정
        email = EmailMessage(subject, message, from_email, recipient_list)
        email.content_subtype = "plain"  # 이메일 본문을 텍스트로 설정
        email.encoding = 'utf-8'  # 인코딩 설정

        try:
            email.send()
            print(f"Email sent to {user.email}")
        except smtplib.SMTPException as e:
            print("Error: unable to send email", e)





#####게시물삭제#####
class PostDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="사용자의 게시물 삭제 API 입니다.",
        operation_summary="게시물 삭제",
        responses={204: "No Content", 401: "Unauthorized", 404: "Not Found"}
    )
    def delete(self, request, post_id):
        post = get_object_or_404(Post, id=post_id, user=request.user)
        post.delete()
        return Response({"message": "게시물이 성공적으로 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)





#####댓글 생성#####
class CommentCreateView(generics.CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_id')
        post = Post.objects.get(id=post_id)
        comment = serializer.save(user=self.request.user, post=post)
        if comment.protector:
            comment.content = f"{comment.content}"
        comment.save()

    @swagger_auto_schema(
        operation_description="게시물에 댓글 작성 API 입니다.",
        operation_summary="댓글 작성",
        request_body=CommentSerializer,
        responses={201: CommentSerializer, 400: "Bad Request"}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)






#####댓글 삭제#####
class CommentDeleteView(generics.DestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        post_id = self.kwargs.get('post_id')
        comment_id = self.kwargs.get('pk')
        comment = get_object_or_404(Comment, id=comment_id, post_id=post_id, user=self.request.user)
        return comment
    
    @swagger_auto_schema(
        operation_description="댓글 삭제 API 입니다.",
        operation_summary="댓글 삭제",
        responses={204: "No Content", 401: "Unauthorized", 403: "Forbidden", 404: "Not Found"}
    )
    def delete(self, request, *args, **kwargs):
        comment = self.get_object()
        self.perform_destroy(comment)
        return Response({"message": "삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)
   




#####메인페이지(date기준 오름차순 사용자의 모든 게시물 조회) + 최근 10개의 게시물 기준 평균 달성률 추가#####
class UserPostListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="사용자의 모든 게시물 조회 (날짜 기준 오름차순) 및 최근 10개의 게시물 기준 평균 달성률 API 입니다.",
        operation_summary="메인페이지",
        responses={
            200: openapi.Response(
                description="사용자의 게시물 및 평균 달성률",
                examples={
                    "application/json": {
                        "posts": [
                            {
                                "id": 1,
                                "date": "2023-01-01",
                                "medication_today": True,
                                "exercise_time": 30,
                                "meal_count": 3,
                                "sleep_time": 8,
                                "daily_summary": "Good day",
                                "achievement_rate_value": 80
                            },
                        ],
                        "TenDaysAverage": 85.5
                    }
                }
            ),
            401: "Unauthorized"
        }
    )
    def get(self, request):
        # 게시물을 날짜 기준 오름차순으로 정렬
        posts = Post.objects.filter(user=request.user).order_by('-date')
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
   




#####상세 페이지(사용자의 특정 한 페이지 조회 (게시물 id 이용))#####
class PostDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="사용자의 특정 게시물 조회 API 입니다.",
        operation_summary="특정 게시물 조회",
        responses={200: PostDetailSerializer, 401: "Unauthorized", 404: "Not Found"}
    )
    def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id, user=request.user)
        serializer = PostDetailSerializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)
    




#####상세 페이지(특정 한페이지의 모든 댓글 조회(생성시간 기준 정렬))#####
class CommentListView(generics.ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        return Comment.objects.filter(post_id=post_id).order_by('created_at')

    @swagger_auto_schema(
        operation_description="특정 게시물의 모든 댓글 조회 API 입니다.",
        operation_summary="댓글 목록 조회",
        responses={200: CommentSerializer(many=True), 401: "Unauthorized", 404: "Not Found"}
    )
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)




#####보고싶어 버튼#####
class MissEmailNotificationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="사용자에게 '보고싶어' 이메일 알림 전송 API 입니다.",
        operation_summary="보고싶어 버튼",
        responses={200: "Success", 404: "Not Found"}
    )
    def get(self, request):
        user_id = request.user.id
        user_profile = get_object_or_404(CustomUser, id=user_id)
        
        user_name = user_profile.username  


        email_subject = '< 다햇슈로부터 보고싶어 알림이 도착했습니다! >'
        email_message = f'{user_name}님께서 보호자님의 연락을 기다리고 있습니다.\n빠른 연락을 부탁드립니다 :)\n\nfrom 다햇슈'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user_profile.email]

        email = EmailMessage(email_subject, email_message, from_email, recipient_list)
        email.content_subtype = "plain"
        email.encoding = 'utf-8'

        try:
            email.send()
            print(f"Email sent to {user_profile.email}")
        except smtplib.SMTPException as e:
            print("Error: unable to send email", e)

        return Response({'message': '보고싶어 알림이 성공적으로 전송되었습니다.'})
    










'''
#댓글 수정
class CommentUpdateView(generics.UpdateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAdminUser]

    @swagger_auto_schema(
        operation_description="댓글 수정 API 입니다.",
        operation_summary="댓글 수정",
        request_body=CommentSerializer,
        responses={200: CommentSerializer, 401: "Unauthorized", 403: "Forbidden", 404: "Not Found"}
    )
    def get_object(self):
        comment = super().get_object()
        if comment.user != self.request.user:
            raise PermissionDenied("수정 권한이 없습니다.")
        return comment
'''

'''
class PostListView(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="사용자의 모든 게시물 목록 조회 API 입니다.",
        operation_summary="게시물 목록 조회",
        responses={200: PostDetailSerializer(many=True), 401: "Unauthorized"}
    )
    def get_queryset(self):
        return Post.objects.filter(user=self.request.user).order_by('-date')
'''
