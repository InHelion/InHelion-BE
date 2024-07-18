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
