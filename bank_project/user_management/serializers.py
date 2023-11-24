from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import User

from rest_framework.response import Response
from rest_framework import status

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','email','password','user_role']
    def create(self, validated_data):
        username=validated_data['username']
        email=validated_data['email']
        password=validated_data['password']
        user_role=validated_data['user_role']
        user = User.objects.create_user(username=username, email=email, password=password, user_role=user_role)
        user.save()
        return user   
       



       

    