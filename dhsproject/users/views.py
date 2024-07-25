from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.shortcuts import get_object_or_404
from .models import CustomUser
from .serializers import UserSerializer

######회원 가입#####
@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True): # 객체가 유효할시 객체 생성
        user = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#####로그인#####
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    identifier = request.data.get('identifier')
    password = request.data.get('password')

    user = authenticate(username=identifier, password=password) # 인증성공시 토큰 생성
    if user is None:
        return Response({'message': '아이디 또는 비밀번호가 일치하지 않습니다.'}, status=status.HTTP_401_UNAUTHORIZED)

    refresh = RefreshToken.for_user(user)
    update_last_login(None, user)
    return Response({
        'refresh_token': str(refresh),
        'access_token': str(refresh.access_token),
        'user_id': user.pk,
        'username': user.username
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    identifier = request.data.get('identifier')
    password = request.data.get('password')

    user = authenticate(username=identifier, password=password)
    if user is None:
        return Response({'message': '아이디 또는 비밀번호가 일치하지 않습니다.'}, status=status.HTTP_401_UNAUTHORIZED)
    return Response({"message": "로그아웃 되었습니다."}, status=status.HTTP_205_RESET_CONTENT)

#####사용자 정보 조회, 정보 수정#####
class ProfileUpdateAPIView(APIView):
    def get(self, request, pk):  # 사용자 조회
        user = get_object_or_404(CustomUser, pk=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def put(self, request, pk):  # 사용자 정보 업데이트
        user = get_object_or_404(CustomUser, pk=pk)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User updated successfully", "data": serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)