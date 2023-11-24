from rest_framework import permissions
from rest_framework import response
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework import status  

class AllUsers(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True
        return False

class ManagerOnly(permissions.BasePermission):
    def has_permission(self, request,view):
        if request.user.user_role=="manager":
            return True
        else:
         return False  
         
class StaffOnly(permissions.BasePermission):
    def has_permission(self, request,view):
        if request.user.user_role=="staff":
            return True
        else:
          raise PermissionDenied('only staff allowed')
        
class CustomerOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        # if request.user.is_authenticated:
            if request.user.user_role == "customer":
                return True
        # return False
    
class ManagerAndStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.user_role=="staff" or request.user.user_role=="manager" :
            return True
        
class CustomerAndStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.user_role=="staff" or request.user.user_role=="customer" :
            return True