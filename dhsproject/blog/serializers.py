from rest_framework import serializers
from .models import Post, Comment

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

class CommentSerializer(serializers.ModelSerializer):
    protector = serializers.BooleanField(required=False)

    class Meta:
        model = Comment
        fields = ['id', 'post_id', 'content', 'protector', 'created_at']
        read_only_field = ['user_id', 'created_at']

    def create(self, validated_data):
        request = self.context.get('request', None)
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)
