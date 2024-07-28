from django.contrib.auth.models import AbstractUser
from django.db import models

#유저 모델 정의 (identifier, email 중복 금지 설정)
class CustomUser(AbstractUser):
    identifier = models.CharField(max_length=30, unique=True) # 아이디 (id와 겹칠 가능성 피하기 위해 identifier로 설정)
    password = models.CharField(max_length=128)
    username = models.CharField(max_length=15)  # 사용자 이름
    email = models.EmailField(unique=True)
    birth = models.DateField()  # 생년월일
    gender = models.CharField(max_length=1, choices=[('m', 'Male'), ('w', 'Female')])  # 성별
    meals = models.IntegerField()  # 끼니
    exercises = models.IntegerField()  # 운동
    medications = models.IntegerField()  # 약
    sleep = models.IntegerField()  # 수면

    USERNAME_FIELD = 'identifier'  # 로그인 시 사용할 필드
    REQUIRED_FIELDS = ['password', 'username', 'email', 'birth', 'gender', 'meals', 'exercises', 'medications', 'sleep']  
    
    # 장고 기본 User 모델의 필드와 충돌을 피하기 위해 related_name을 설정
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',  # 기존 'user_set'에서 변경
        blank=True,
        help_text='The groups this user belongs to.',
        related_query_name='customuser'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',  # 기존 'user_set'에서 변경
        blank=True,
        help_text='Specific permissions for this user.',
        related_query_name='customuser'
    )

    def __str__(self):
        return self.username
