from rest_framework import serializers
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('identifier', 'password', 'username', 'email', 'birth', 'gender', 'meals', 'exercises', 'medications', 'sleep')
        extra_kwargs = {'password': {'write_only': True}} # 비밀번호는 응답에 포함 X

    def create(self, validated_data):
        user = CustomUser.objects.create(
            identifier=validated_data['identifier'],
            username=validated_data['username'],
            email=validated_data['email'],
            birth=validated_data['birth'],
            gender=validated_data['gender'],
            meals=validated_data['meals'],
            exercises=validated_data['exercises'],
            medications=validated_data['medications'],
            sleep=validated_data['sleep']
        )
        user.set_password(validated_data['password'])  # 비밀번호 해시화
        user.save()
        return user

    def update(self, instance, validated_data):
        instance.identifier = validated_data.get('identifier', instance.username)
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.birth = validated_data.get('birth', instance.birth)
        instance.gender = validated_data.get('gender', instance.gender)
        instance.meals = validated_data.get('meals', instance.meals)
        instance.exercises = validated_data.get('exercises', instance.exercises)
        instance.medications = validated_data.get('medications', instance.medications)
        instance.sleep = validated_data.get('sleep', instance.sleep)
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])  # 비밀번호 해시화
        instance.save()
        return instance