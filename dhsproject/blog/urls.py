from django.urls import path
from .views import PostCreateView, PostListView

urlpatterns = [
    path('create/', PostCreateView.as_view(), name='post-create'),
    path('', PostListView.as_view(), name='post-list'),
]