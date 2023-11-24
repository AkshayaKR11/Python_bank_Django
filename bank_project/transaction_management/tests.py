from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate
from rest_framework import status
from .models import Transaction
from .views import TransactionView,WithdrawView,DepositView
from account_management.models import Account
from user_management.models import User


class TransactionViewTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.customer_user = User.objects.create_user(username='customer', password='password', email='customer@gmail.com', user_role='customer')
        self.staff_user = User.objects.create_user(username='staff', password='password', email='staff@gmail.com', user_role='staff')

    def test_get_transactions_successful(self):
        account = Account.objects.create(account_number='123ABC', user=self.customer_user, account_type='Savings', account_balance=1000, status='Approved')
        Transaction.objects.create(account=account, transaction_type='Deposit', transaction_amount=500)
        Transaction.objects.create(account=account, transaction_type='Withdraw', transaction_amount=200)
        request = self.factory.get(f'/transaction/transaction/{account.account_number}/')
        force_authenticate(request,self.staff_user)
        view = TransactionView.as_view()
        response = view(request, account_number=account.account_number)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_transactions_not_found(self):
        request = self.factory.get('/transaction/transaction/9999/')
        force_authenticate(request,self.staff_user)
        view = TransactionView.as_view()
        response = view(request, account_number=9999)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)  

    def test_get_transactions_unauthenticated_user(self):
        account = Account.objects.create(account_number='123456', user=self.customer_user, account_type='Savings', account_balance=1000, status='Approved')
        Transaction.objects.create(account=account, transaction_type='Deposit', transaction_amount=500)
        request = self.factory.get(f'/transaction/transaction/{account.account_number}/')
        view = TransactionView.as_view()
        response = view(request, account_number=account.account_number)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class WithdrawViewTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.customer_user = User.objects.create_user(username='customer', password='password', email='customer@gmail.com', user_role='customer')

    def test_withdraw_successful(self):
        account = Account.objects.create(account_number='123ABC', user=self.customer_user, account_type='Savings', account_balance=1000, status='Approved')
        request = self.factory.post(f'/transaction/withdraw/{account.account_number}/', data={'amount': 500}, format='json')
        force_authenticate(request,user=self.customer_user)
        view = WithdrawView.as_view()
        response = view(request, account_number=account.account_number)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        account.refresh_from_db()  
        self.assertEqual(account.account_balance, 500)

    def test_withdraw_account_not_found(self):
        request = self.factory.post('/transaction/withdraw/8888/', data={'amount': 500}, format='json')
        force_authenticate(request,user=self.customer_user)
        view = WithdrawView.as_view()
        response = view(request, account_number=8888)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_withdraw_invalid_amount(self):
        account = Account.objects.create(account_number='123ABC', user=self.customer_user, account_type='Savings', account_balance=2000, status='Approved')
        request = self.factory.post(f'/transaction/withdraw/{account.account_number}/', data={'amount': -500}, format='json')
        force_authenticate(request,user=self.customer_user)
        view = WithdrawView.as_view()
        response = view(request, account_number=account.account_number)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        account.refresh_from_db()  
        self.assertEqual(account.account_balance,2000)

    def test_withdraw_insufficient_balance(self):
        account = Account.objects.create(account_number='123ABC', user=self.customer_user, account_type='Savings', account_balance=100, status='Approved')
        request = self.factory.post(f'/transaction/withdraw/{account.account_number}/', data={'amount': 500}, format='json')
        force_authenticate(request,user=self.customer_user)
        view = WithdrawView.as_view()
        response = view(request, account_number=account.account_number)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        account.refresh_from_db()  
        self.assertEqual(account.account_balance, 100)

    def test_withdraw_not_approved(self):
        account = Account.objects.create(account_number='123ABC', user=self.customer_user, account_type='Savings', account_balance=1000, status='Pending')
        request = self.factory.post(f'/transaction/withdraw/{account.account_number}/', data={'amount': 500}, format='json')
        force_authenticate(request,user=self.customer_user)
        view = WithdrawView.as_view()
        response = view(request, account_number=account.account_number)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        account.refresh_from_db()  
        self.assertEqual(account.account_balance, 1000)

class DepositViewTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.customer_user = User.objects.create_user(username='customer', password='password', email='customer@gmail.com', user_role='customer')
    def test_deposit_successful(self):
        account = Account.objects.create(account_number='123ABC', user=self.customer_user, account_type='Savings', account_balance=1000, status='Approved')
        request = self.factory.post(f'/transaction/deposit/{account.account_number}/', data={'amount': 500}, format='json')
        force_authenticate(request,user=self.customer_user)
        view = DepositView.as_view()
        response = view(request, account_number=account.account_number)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        account.refresh_from_db()  
        self.assertEqual(account.account_balance, 1500)

    def test_deposit_account_not_found(self):
        request = self.factory.post('/transaction/deposit/8888/', data={'amount': 500}, format='json')
        force_authenticate(request,user=self.customer_user)
        view = DepositView.as_view()
        response = view(request, account_number=8888)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_deposit_invalid_amount(self):
        account = Account.objects.create(account_number='123ABC', user=self.customer_user, account_type='Savings', account_balance=2000, status='Approved')
        request = self.factory.post(f'/transaction/deposit/{account.account_number}/', data={'amount': -500}, format='json')
        force_authenticate(request,user=self.customer_user)
        view = DepositView.as_view()
        response = view(request, account_number=account.account_number)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        account.refresh_from_db()  
        self.assertEqual(account.account_balance,2000)

    def test_deposit_not_approved(self):
        account = Account.objects.create(account_number='123ABC', user=self.customer_user, account_type='Savings', account_balance=1000, status='Pending')
        request = self.factory.post(f'/transaction/deposit/{account.account_number}/', data={'amount': 500}, format='json')
        force_authenticate(request,user=self.customer_user)
        view = WithdrawView.as_view()
        response = view(request, account_number=account.account_number)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        account.refresh_from_db()  
        self.assertEqual(account.account_balance, 1000)


    
    