from django.urls import path
from .views import signup, login, logout, ProfileUpdateAPIView,check_identifier, check_email

urlpatterns = [
    path('signup/', signup, name='signup'), #회원가입
    path('login/', login, name='login'), #로그인 
    path('logout/', logout, name='logout'), #로그아웃
    path('profile/', ProfileUpdateAPIView.as_view(), name='profile_update'), #회원정보 조회, 회원정보 수정
    path('check_identifier/', check_identifier, name='check_identifier'), #아이디 중복검사
    path('check_email/', check_email, name='check_email'), #이메일 중복검사
]