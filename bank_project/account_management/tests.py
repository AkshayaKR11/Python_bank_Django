from django.test import TestCase
from rest_framework.test import APIRequestFactory,APIClient
from rest_framework.test import force_authenticate
from rest_framework import status
from .models import Account
from .views import AccountCreate,AccountView,StatusView,ApproveView,CloseAccount,AccountListView
from user_management.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.views import TokenObtainPairView



class TokenGenerationAndUsageTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_token_generation(self):
        client = APIClient()
        response = client.post('/login/', {'username': 'testuser', 'password': 'testpassword'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)

    def test_protected_resource_access(self):
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)
        factory = APIRequestFactory()
        request = factory.get('/account/creation/')  
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {access_token}' 
        view = AccountCreate.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 403)
        
class AccountCreateTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.customer_user = User.objects.create_user(username='customer', password='password', email='customer@gmail.com',user_role='customer')
        self.staff_user = User.objects.create_user(username='staff', password='password', email='staff@gmail.com',user_role='staff')
    def test_account_create_successful(self):
        
        data = {
            'account_type': 'testtype',
            'account_balance': 0,
            'user': self.customer_user.id
        }

        request = self.factory.post('/account/creation/', data, format='json')
        force_authenticate(request, user=self.customer_user)
        view = AccountCreate.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_account_create_invalid(self): 
        data = {
            'account_type': '',
            'account_balance': -8,
            'user': self.customer_user.id
        }
        request = self.factory.post('/account/creation/', data, format='json')
        force_authenticate(request, user=self.customer_user)
        view = AccountCreate.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)    

    def test_account_create_not_access(self): 
        data = {
            'account_type': 'testtype',
            'account_balance': 8000,
            'user': self.customer_user.id
        }
        request = self.factory.post('/account/creation/', data, format='json')
        force_authenticate(request, user=self.staff_user)
        view = AccountCreate.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN) 

class AccountViewTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.manager_user = User.objects.create_user(username='manager_staff', password='password', email='managerstaff@gmail.com',user_role='manager')

    def test_get_account_list_successful(self):
        account1 = Account.objects.create(account_type='type1', account_balance=1000,user=self.manager_user)
        account2 = Account.objects.create(account_type='type2', account_balance=2000,user=self.manager_user)

        request = self.factory.get('/account/view/')
        force_authenticate(request,user=self.manager_user)
        view = AccountView.as_view()
        response = view(request)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2) 

    def test_get_account_detail_successful(self):
        account = Account.objects.create(account_type='type1', account_balance=1000,user=self.manager_user)

        request = self.factory.get(f'/account/view/{account.id}/')
        force_authenticate(request,user=self.manager_user)
        view = AccountView.as_view()
        response = view(request, id=account.id)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        

    def test_get_account_detail_not_found(self):
        request = self.factory.get('/account/view/999/') 
        force_authenticate(request,user=self.manager_user) 
        view = AccountView.as_view()
        response = view(request, id=999)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
class StatusViewTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.customer_user = User.objects.create_user(username='customer', password='password', email='customer@gmail.com',user_role='customer')
        Account.objects.create(account_type='type1', account_balance=1000,user=self.customer_user, status='Pending')
        Account.objects.create(account_type='type2', account_balance=2000, user=self.customer_user,status='Approved')
        Account.objects.create(account_type='type3', account_balance=3000,user=self.customer_user, status='Closed')

    def test_get_accounts_by_status_successful(self):
        request = self.factory.get('/account/status/',{'status': 'Approved'})
        view = StatusView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        

    def test_get_accounts_by_status_no_match(self):
        request = self.factory.get('/account/status/', {'status': 'NonExistentStatus'})
        view = StatusView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        

    def test_get_accounts_by_status_invalid_param(self):
        request = self.factory.get('/account/status/', {'invalid_param': 'Approved'})
        view = StatusView.as_view()
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

class ApproveViewTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.staff_user = User.objects.create_user(username='staff', password='password', email='staff@gmail.com', user_role='staff')
        self.customer_user = User.objects.create_user(username='customer', password='password', email='customer@gmail.com', user_role='customer')

    def test_approve_account_successful(self):
        account = Account.objects.create(account_type='type1', account_balance=1000,user=self.customer_user,status='Pending')
        email = 'staff@gmail.com'  
        request = self.factory.patch(f'/approveaccount/{email}/{account.id}/', data={'status': 'Approved'}, format='json')
        force_authenticate(request,user=self.staff_user)
        view = ApproveView.as_view()
        response = view(request, email=email, id=account.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_approve_account_not_staff(self):
        account = Account.objects.create(account_type='type1', account_balance=1000, user=self.customer_user,status='Pending')
        email = 'customer@gmail.com' 
        request = self.factory.patch(f'/approveaccount/{email}/{account.id}/', data={'status': 'Approved'}, format='json')
        view = ApproveView.as_view()
        force_authenticate(request,user=self.customer_user)
        response = view(request, email=email, id=account.id)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_approve_account_user_not_found(self):
        account = Account.objects.create(account_type='type1', account_balance=1000,user=self.customer_user, status='Pending')
        email = 'nonexistent@gmail.com' 
        request = self.factory.patch(f'/approveaccount/{email}/{account.id}/', data={'status': 'Approved'}, format='json')
        force_authenticate(request,user=self.staff_user)  
        view = ApproveView.as_view()
        response = view(request, email=email, id=account.id)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        account.refresh_from_db()  
    def test_approve_account_not_found(self):
        email = 'staff@gmail.com'  
        request = self.factory.patch(f'/approveaccount/{email}/999/', data={'status': 'Approved'}, format='json')
        force_authenticate(request,user=self.staff_user)
        view = ApproveView.as_view()
        response = view(request, email=email, id=999)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
class CloseAccountTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.staff_user = User.objects.create_user(username='staff', password='password', email='staff@gmail.com', user_role='staff')
        self.customer_user = User.objects.create_user(username='customer', password='password', email='customer@gmail.com', user_role='customer')

    def test_close_account_successful(self):
        account = Account.objects.create(account_type='type1', account_balance=1000, user=self.customer_user, status='Approved')
        request = self.factory.patch(f'/close/{account.id}/', data={}, format='json')
        force_authenticate(request,self.customer_user)
        view = CloseAccount.as_view()
        response = view(request, id=account.id)
        self.assertEqual(response.status_code,status.HTTP_200_OK)

    def test_close_account_not_found(self):
        request = self.factory.patch('/close/999/', data={}, format='json')
        force_authenticate(request,self.customer_user)
        view = CloseAccount.as_view()
        response = view(request, id=999)
        self.assertEqual(response.status_code,status.HTTP_404_NOT_FOUND)

class AccountListViewTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(username='test_user', password='testpassword',user_role='customer')
        self.manager=User.objects.create_user(username='test_manager',password='managerpassword',user_role='manager')
        self.account1 = Account.objects.create(account_type='Type1',user=self.user,account_balance=100)
        self.account2 = Account.objects.create(account_type='Type2',user=self.user,account_balance=400)
        self.account3 = Account.objects.create(account_type='Type3',user=self.user,account_balance=300)
        self.account4 = Account.objects.create(account_type='AnotherType',user=self.user,account_balance=200)

    def test_account_list_view_with_pagination(self):
        url = '/account/list' 
        request = self.factory.get(url)
        force_authenticate(request,user=self.manager)
        view = AccountListView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)

    def test_account_list_view_with_search_filter(self):
        url = '/account/list/' 
        request = self.factory.get(url, {'search': 'Type2'})
        force_authenticate(request,self.manager)
        view = AccountListView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['account_type'], 'Type2')