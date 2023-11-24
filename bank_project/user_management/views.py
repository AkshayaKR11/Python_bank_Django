

from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import UserSerializer
from rest_framework.response import Response
from rest_framework import generics  
from .models import User   
from account_management.models import Account
from rest_framework import status  
from django_filters.rest_framework import DjangoFilterBackend 
from .permissions import ManagerOnly,StaffOnly,ManagerAndStaff
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        password = request.data.get('password')  
        try:
            validate_password(password)
        except ValidationError as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid():
            serializer.save() 
            return Response('Successfully Register!', status=status.HTTP_201_CREATED)  
        return Response({"message":"Data is not valid","data":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def get_token(cls,user:User):
        token=super().get_token(user)
        token['name']=user.username
        token['user_role']=user.user_role
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        data['access'] = str(refresh.access_token)
        data['refresh'] = str(refresh)
        data['user_role'] = self.user.user_role  
        return data
    
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class=CustomTokenObtainPairSerializer

class UserList(generics.ListAPIView):
    # permission_classes=[ManagerAndStaff]
    queryset = User.objects.all() 
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user_role']

class CustomerUpdateView(APIView):
   permission_classes=[StaffOnly]
   def patch(self,request,id):
        result=User.objects.get(id=id)
        if result.user_role=='customer':
            serializer=UserSerializer(result,data=request.data,partial=True)
            if serializer.is_valid():  
                serializer.save()  
                return Response({"status": "successfully updated", "data": serializer.data}, status=status.HTTP_200_OK)  
            else:  
                return Response({"status": "error", "data": "Updation Failed"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"Staff can only update customer"}, status=status.HTTP_403_FORBIDDEN)

class StaffUpdateView(APIView):
   permission_classes=[ManagerOnly]
   def patch(self,request,id):
        result=User.objects.get(id=id)
        if result.user_role=='staff':
            serializer=UserSerializer(result,data=request.data,partial=True)
            if serializer.is_valid():  
                serializer.save()  
                return Response({"status":"Updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)  
            else:  
                return Response({"status": "error", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"Manager can only update staff"}, status=status.HTTP_403_FORBIDDEN)
               
    
        
