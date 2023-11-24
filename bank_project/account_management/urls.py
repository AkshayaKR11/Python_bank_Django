from django.urls import path
from .views import AccountView,AccountCreate,CloseAccount,StatusView,AccountListView,ApproveView,AccountViewUser,AccountApproved
urlpatterns = [
  
    path('creation/',AccountCreate.as_view()),
    path('view/<int:id>/',AccountView.as_view()),
    path('status/',StatusView.as_view()),
    path('approveaccount/<int:id>',ApproveView.as_view()),
    path('list/',AccountListView.as_view()),
    path('close/<int:id>/',CloseAccount.as_view()), 
    path('account_view/',AccountViewUser.as_view()), 
    path('approved_account_view/',AccountApproved.as_view()), 

]