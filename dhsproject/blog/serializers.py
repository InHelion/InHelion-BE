from rest_framework import serializers
from .models import Post

class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('id', 'date', 'medication_today', 'exercise_time', 'meal_count', 'sleep_time', 'daily_summary')

class PostDetailSerializer(serializers.ModelSerializer):
    identifier = serializers.ReadOnlyField(source='user.identifier')
    username = serializers.ReadOnlyField(source='user.username')
    achievement_rate = serializers.SerializerMethodField()
    class Meta:
        model = Post
        fields = (
            'id', 'date', 'medication_today', 'exercise_time', 'meal_count', 'sleep_time', 'daily_summary',
            'identifier', 'username', 'user_meals', 'user_exercises', 'user_medications', 'user_sleep', 'achievement_rate'
        )

    def get_achievement_rate(self, obj):
        return obj.achievement_rate()
    
###메인페이지(date 기준 사용자 모든 게시물 조회)용 시리얼라이저
class PostListSerializer(serializers.ModelSerializer):
    achievement_rate = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('id', 'date', 'medication_today', 'exercise_time', 'meal_count', 'sleep_time', 'daily_summary', 'achievement_rate')

    def get_achievement_rate(self, obj):
        return obj.achievement_rate()
