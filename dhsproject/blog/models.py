from django.db import models
from django.conf import settings

class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    date = models.DateField()  # 글 작성 날짜를 사용자가 입력할 수 있도록 변경
    meal_count = models.IntegerField()  # 끼니 수
    exercise_time = models.IntegerField()  # 오늘 운동 시간 (분단위)
    medication_today = models.IntegerField()  # 오늘의 약 갯수 
    sleep_time = models.IntegerField()  # 오늘의 수면 시간 (시간 단위)
    daily_summary = models.TextField()  # 하루 마무리 소감 (최소 한 줄 이상)
    
    # 사용자가 게시물 작성 시점의 정보를 저장하는 필드
    user_meals = models.IntegerField()
    user_exercises = models.IntegerField()
    user_medications = models.IntegerField()
    user_sleep = models.IntegerField()
    
    def __str__(self):
        return f"{self.user.username} - {self.date}"
    
    # 달성률 필드
    def achievement_rate(self):
        total = 0
        if self.medication_today == self.user_medications:
            total += 25
        if self.exercise_time >= self.user_exercises:
            total += 25
        if self.meal_count == self.user_meals:
            total += 25
        if self.user_sleep - 1 <= self.sleep_time <= self.user_sleep + 1:
            total += 25
        
        return total

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    protector = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        if self.protector:
            return f"Protector - {self.content[:30]}"
        else:
            return f"{self.user.username} - {self.content[:30]}"