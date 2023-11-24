from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response  
from django.http import HttpResponse
from rest_framework import status  
from rest_framework import generics
from .models import Transaction
from .serializers import TransactionSerializer
from account_management.serializers import AccountSerializer
from account_management.models import Account
import csv
from rest_framework import filters
from user_management.permissions import AllUsers,CustomerOnly
from django.db import transaction


class TransactionView(APIView):
    def get(self,request):
        try:
            transactions = Transaction.objects.order_by('-transaction_date')
            serializer = TransactionSerializer(transactions, many=True)
            return Response({'success': 'success', "members":serializer.data}, status=200) 
        except Account.DoesNotExist:
            return Response({"status": "Account not found"}, status=status.HTTP_404_NOT_FOUND)
        
class TransactionViewAccount(APIView):
    def get(self, request):
        try:
            user_id=request.user.id
            account_obj = Account.objects.get(user=user_id)
            transactions = Transaction.objects.filter(account=account_obj.id)
            serializer = TransactionSerializer(transactions, many=True)
            return Response({'success': 'success', 'transactions': serializer.data}, status=status.HTTP_200_OK)
        except Account.DoesNotExist:
            return Response({"status": "Account not found"}, status=status.HTTP_404_NOT_FOUND)
        
class WithdrawView(APIView):
    permission_classes=[CustomerOnly]
    serializer_class = AccountSerializer

    # def get_queryset(self):
    #     account_number = self.kwargs.get('account_number')
    #     return Account.objects.filter(account_number=account_number)

    def post(self, request):
        amount = int(request.data.get('amount'))
        userid=request.user.id
        with transaction.atomic():
         try:
            account = Account.objects.get(user=userid)
            if account.status=='Approved':
                if account.account_balance >= amount: 
                    if amount > 0:
                        account.account_balance -= amount
                        account.save()
                        transactions = Transaction(transaction_type="withdraw", transaction_amount=amount,account_id=account.id)
                        transactions.save()
                        return Response({'message': f'Withdrawn ${amount} from account {account.account_number}'}, status=status.HTTP_200_OK)
                    else:
                     return Response({'message': 'Invalid amount'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                 return Response({'message': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'message': 'Sorry!!! Make sure that your Account is approved'}, status=status.HTTP_400_BAD_REQUEST)
         except Account.DoesNotExist:
            return Response({'message': 'No Account found'}, status=status.HTTP_404_NOT_FOUND)

class DepositView(APIView):
    permission_classes=[CustomerOnly]
    serializer_class = AccountSerializer
    def post(self, request):
        amount = int(request.data.get('amount'))
        if amount is None:
            return Response({'message': 'Amount cannot be None'}, status=status.HTTP_400_BAD_REQUEST)
        userid=request.user.id
        with transaction.atomic():
         try:
            account = Account.objects.get(user=userid)
            account_number=account.account_number
            if account.status=='Approved':
                print("Amount:", amount)
                if amount>0:
                    account.account_balance += amount
                    account.save()
                    transactions = Transaction(transaction_type="deposit", transaction_amount=amount,account_id=account.id)
                    transactions.save()
                    return Response({'message': f'Deposit ${amount} to account {account_number}'}, status=status.HTTP_200_OK)
                else:
                    return Response({'message': 'Invalid '}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'message': 'Sorry!!Make sure that your Account is approved'}, status=status.HTTP_400_BAD_REQUEST)
         except Account.DoesNotExist:
            return Response({'message': 'Account not found'}, status=status.HTTP_404_NOT_FOUND)


class TransactionHistoryDownload(APIView):
    permission_classes=[AllUsers]
    def get(self, request, account_number):
        try:

            account = Account.objects.get(account_number=account_number)  
            transactions = Transaction.objects.filter(account=account)  
            if account.status=='Approved':
                if transactions:
                    response = HttpResponse(content_type='text/csv')
                    response['Content-Disposition'] = f'attachment; filename="transactions_account_{account_number}.csv"'

                    writer = csv.writer(response)
                    writer.writerow(["Account Number", "Date", "Type", "Amount"])

                    for transaction in transactions:
                        serializer = TransactionSerializer(transaction)
                        writer.writerow([
                            account.account_number, 
                            serializer.data['transaction_date'],
                            serializer.data['transaction_type'],
                            serializer.data['transaction_amount'],
                    ])

                    return response
                else:
                    return Response({'message': 'No transactions found for the account'}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({'message': 'Sorry!!Make sure that your Account is approved'}, status=status.HTTP_400_BAD_REQUEST)
        except Account.DoesNotExist:
            return Response({'message': 'Account not found'}, status=status.HTTP_404_NOT_FOUND)