
from rest_framework import generics, permissions, status
from .models import Post, Comment
from .serializers import PostCreateSerializer, PostDetailSerializer, PostListSerializer,CommentSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

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

###메인페이지(date기준 오름차순 사용자의 모든 게시물 조회)
class UserPostListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        posts = Post.objects.filter(user=request.user).order_by('date')
        serializer = PostListSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
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
