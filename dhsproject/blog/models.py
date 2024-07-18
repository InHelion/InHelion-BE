from django.db import models
from django.conf import settings

class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    date = models.DateField()  # 글 작성 날짜를 사용자가 입력할 수 있도록 변경
    medication_today = models.IntegerField()  # 오늘의 약 갯수
    exercise_time = models.IntegerField()  # 오늘 운동 시간 (분단위)
    meal_count = models.IntegerField()  # 끼니 수
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
        # 약
        if self.user_medications > 0:
            medication_rate = (self.medication_today / self.user_medications) * 25
            total += min(medication_rate, 25) 
        
        # 운동
        if self.user_exercises > 0:
            exercise_rate = (self.exercise_time / self.user_exercises) * 25
            total += min(exercise_rate, 25) 
        
        # 끼니
        if self.user_meals > 0:
            meal_rate = (self.meal_count / self.user_meals) * 25
            total += min(meal_rate, 25) 
        
        # 수면
        if self.user_sleep > 0:
            sleep_rate = (self.sleep_time / self.user_sleep) * 25
            total += min(sleep_rate, 25)
          

        return round(total, 2)