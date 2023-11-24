from django.contrib import admin
from .models import User
class AdminView(admin.ModelAdmin):
    list_display=['username','email','password',]
    def get_queryset(self,request):
        queryset=super(AdminView,self).get_queryset(request)
        queryset=queryset.filter(user_role='manager')|queryset.filter(user_role='staff')
        return queryset
admin.site.register(User,AdminView)