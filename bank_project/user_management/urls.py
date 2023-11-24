from django.urls import path
from .views import RegisterView,UserList,CustomerUpdateView,StaffUpdateView

urlpatterns = [
    path('user_register/', RegisterView.as_view(), name="sign_up"),
    path('userview/', UserList.as_view(), name="filter_list"),
    path('customer_update/<int:id>',CustomerUpdateView.as_view()),
    path('staff_update/',StaffUpdateView.as_view()),

   
]
