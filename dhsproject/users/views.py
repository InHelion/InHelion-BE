from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.shortcuts import get_object_or_404
from .models import CustomUser
from .serializers import UserSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi




#####회원가입#####
@swagger_auto_schema(
    method='post',
    operation_description="사용자 회원가입 api 입니다.",
    operation_summary="회원가입", 
    request_body=UserSerializer,
    responses={201: UserSerializer, 400: "Bad Request"}
)
@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True): # 객체가 유효할시 객체 생성
        user = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





#####로그인#####
@swagger_auto_schema(
    method='post',
    operation_description="사용자 로그인 api 입니다.",
    operation_summary="로그인", 
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'identifier': openapi.Schema(type=openapi.TYPE_STRING, description='사용자 ID'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='비밀번호')
        }
    ),
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'refresh_token': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh Token'),
                'access_token': openapi.Schema(type=openapi.TYPE_STRING, description='Access Token'),
                'user_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='User ID'),
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username')
            }
        ),
        401: "Unauthorized"
    }
)
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





#####로그아웃#####
@swagger_auto_schema(
    method='post',
    operation_description="사용자 로그아웃 api입니다.",
    operation_summary="로그아웃", 
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'identifier': openapi.Schema(type=openapi.TYPE_STRING, description='사용자 ID'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='비밀번호')
        }
    ),
    responses={205: "Reset Content", 401: "Unauthorized"}
)
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
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="사용자 정보 조회 api 입니다.",
        operation_summary="사용자 정보 조회", 
        responses={200: UserSerializer, 403: "권한 없음"}
    )
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_description="사용자 정보 수정 api 입니다.",
        operation_summary="사용자 정보 수정", 
        request_body=UserSerializer,
        responses={200: "User updated successfully", 400: "Bad Request", 403: "권한 없음"}
    )
    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User updated successfully", "data": serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    





# ID 중복검사 버튼
@api_view(['POST'])
@permission_classes([AllowAny])
def check_identifier(request):
    identifier = request.data.get('identifier', None)
    
    if identifier and CustomUser.objects.filter(identifier=identifier).exists():
        return Response({'identifier': '이미 사용중인 아이디입니다!'}, status=status.HTTP_409_CONFLICT)
    
    return Response({'identifier': '사용 가능한 아이디입니다!'}, status=status.HTTP_200_OK)


# 이메일 중복검사 버튼
@api_view(['POST'])
@permission_classes([AllowAny])
def check_email(request):
    email = request.data.get('email', None)
    
    if email and CustomUser.objects.filter(email=email).exists():
        return Response({'email': '이미 사용중인 이메일입니다!'}, status=status.HTTP_409_CONFLICT)
    
    return Response({'email': '사용 가능한 이메일입니다!'}, status=status.HTTP_200_OK)