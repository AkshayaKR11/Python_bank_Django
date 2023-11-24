from django.shortcuts import render
from rest_framework.views import APIView
from .models import Account
from rest_framework.response import Response  
from rest_framework import status  
from .serializers import AccountSerializer
from user_management.models import User
from rest_framework import generics
from rest_framework import filters
from rest_framework import permissions
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import NotFound
from user_management.permissions import StaffOnly,ManagerAndStaff,CustomerOnly,CustomerAndStaff
from rest_framework.permissions import IsAuthenticated
import traceback



class StandardResultsSetPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    page_query_param = 'page'
    max_page_size = 100

    def paginate_queryset(self, queryset, request, view=None):
        page_size = self.get_page_size(request)
        if not page_size:
            return None
        paginator = self.django_paginator_class(queryset, page_size)
        page_number = request.query_params.get(self.page_query_param, 1)
        if page_number in self.last_page_strings:
            page_number = paginator.num_pages
        try:
            self.page = paginator.page(page_number)
        except Exception as e:
          
            msg = {
                "code": 400 ,
                "error": "Page out of range"
            }
            raise NotFound(msg)
        if paginator.num_pages > 1 and self.template is not None:
            self.display_page_controls = True
        self.request = request
        return list(self.page)
    
class AccountView(APIView):
    permission_classes=[ManagerAndStaff]
    def get(self,request,id=None):
         if id:
            try:
             result=Account.objects.get(id=id)
             serializers = AccountSerializer(result)  
             return Response({'success': 'success', "members":serializers.data}, status=200)  
            except Account.DoesNotExist:
             return Response({'success': 'not found', }, status=404)           
         result=Account.objects.all()
         serializer=AccountSerializer(result,many=True)
         return Response({'success': 'success', "members":serializer.data}, status=200) 

class AccountViewUser(APIView):
    permission_classes=[CustomerOnly]
    def get(self,request):
        try:
            user_id=request.user.id
            account=Account.objects.get(user=user_id)
            serializer=AccountSerializer(account)
            return Response({'success': 'success', 'results': serializer.data}, status=status.HTTP_200_OK)
        except Account.DoesNotExist:
            return Response({"message": "Account not found"}, status=status.HTTP_404_NOT_FOUND)
        

    
class AccountCreate(APIView): 
    permission_classes=[CustomerOnly,IsAuthenticated]
    def post(self,request):
        serializer=AccountSerializer(data=request.data)
        print(request.user)
        user_obj=User.objects.get(username=request.user)
        print('User Details',user_obj.id)
        print('User Role',user_obj.user_role)
        account=Account.objects.filter(user=request.user)
        if account:
         return Response({"message":"User Already Have one Account"})
        elif serializer.is_valid():
            serializer.save(user=user_obj)
            # Account.save(user=request.user.id)
            return Response({"message": "Account created Successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)  
        else:  
            return Response({"status": "error", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)  

class StatusView(generics.ListAPIView):
    serializer_class = AccountSerializer
    def get_queryset(self):
        status = self.request.query_params.get('status')
        return Account.objects.filter(status=status)

class ApproveView(APIView):   
    permission_classes = [StaffOnly]
    def patch(self,request,id):
        try:
            result=Account.objects.get(id=id)
            print(result) 
            result.status=request.data.get('status')
            result.save()
            return Response({"status": "Account approved", "data": result.status}, status=status.HTTP_200_OK)    
        except Account.DoesNotExist:
                return Response({"message": "Account not Found"},status=status.HTTP_404_NOT_FOUND) 


class AccountListView(generics.ListAPIView):
    
    queryset = Account.objects.all().order_by('id')
    serializer_class = AccountSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['account_type']

class AccountApproved(generics.ListAPIView):
     queryset = Account.objects.filter(status='Approved').order_by('-joined_date')
     serializer_class = AccountSerializer
     pagination_class=StandardResultsSetPagination

class CloseAccount(APIView):
    permission_classes=[CustomerAndStaff]
    def patch(self,request,id):
        try:
            result = Account.objects.get(id=id)
            result.status='closed'
            result.save()
            return Response({"status": "success", "data": "Account closed"}, status=status.HTTP_200_OK)
        except Account.DoesNotExist:
             return Response({"Account not found"},status=status.HTTP_404_NOT_FOUND)
