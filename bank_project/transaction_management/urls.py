from django.urls import path
from .views import TransactionView,WithdrawView,DepositView,TransactionHistoryDownload,TransactionViewAccount
urlpatterns = [
  
    path('transaction/',TransactionView.as_view()),
    path('withdraw/',WithdrawView.as_view()),
    path('deposit/',DepositView.as_view()),
    path('transaction_history/<str:account_number>',TransactionHistoryDownload.as_view()),
    path('transaction_view/',TransactionViewAccount.as_view()),
    
]