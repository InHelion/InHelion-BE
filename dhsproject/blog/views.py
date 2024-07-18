from rest_framework import generics, permissions
from .models import Post
from .serializers import PostCreateSerializer, PostDetailSerializer

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
