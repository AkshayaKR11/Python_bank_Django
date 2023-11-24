from django.test import TestCase
from rest_framework.test import APIRequestFactory
from .views import RegisterView,UserList,CustomerUpdateView,StaffUpdateView
from .admin import AdminView
from rest_framework import status
from .models import User
from rest_framework.test import force_authenticate

factory = APIRequestFactory()

class RegisterViewTestCase(TestCase):
    def test_valid_registration(self):
        data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'testpassword',
            'user_role':'customer'
        }
        request = factory.post('user_register/', data, format='json')
        view = RegisterView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_invalid_registration(self):
        data = {
            'username': '',
            'email': 'invalid_email',
            'password': 'short',
            'user_role':'test'
        }
        request = factory.post('/user_register/', data, format='json')
        view = RegisterView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class UserListTestCase(TestCase):
    def create_dummy_user(self,username,password,email,user_role):
            user_data={
                "username":username,
                "password":password,
                "email":email,
                "user_role":user_role
            }
            return User.objects.create_user(**user_data)

    def test_manager_access(self):
        view = UserList.as_view()
        request = factory.get('/userroleview/', {'user_role': 'customer'})
        manager_user=self.create_dummy_user(username="testmanager",password='testpassword',email='manager@gmail.com',user_role='manager')
        force_authenticate(request, user=manager_user)
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_manager_access(self):
        view = UserList.as_view()
        request = factory.get('/userroleview/', {'user_role': 'customer'})
        staff_user=self.create_dummy_user(username="teststaff",password='testpasword',email='staff@gmail.com',user_role='staff')
        force_authenticate(request, user=staff_user)
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_filter_by_non_user_role(self):
        view = UserList.as_view()
        request = factory.get('/userroleview/', {'user_role': 'cleaner'})
        manager_user=self.create_dummy_user(username="testmanager",password='testpassword',email='manager@gmail.com',user_role='manager')
        force_authenticate(request, user=manager_user)
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class CustomerUpdateViewTestCase(TestCase):
    def create_dummy_user(self,username,password,email,user_role):
            user_data={
                "username":username,
                "password":password,
                "email":email,
                "user_role":user_role
            }
            return User.objects.create_user(**user_data)
    
    def test_staff_access(self):
        view = CustomerUpdateView.as_view()
        customer_user=self.create_dummy_user(username="testcustomer",password='testpasword',email='customer@gmail.com',user_role='customer')
        data={"email":"testemaile@gmail.com"}
        request = factory.patch(f'/customer_update/{customer_user.id}/',data,format='json')  
        staff_user = self.create_dummy_user(username="teststaff", password='testpassword', email='staff@gmail.com', user_role='staff')
        force_authenticate(request, user=staff_user)
        response = view(request,id=customer_user.id)
        user=User.objects.get(id=customer_user.id)
        print(user.email)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_staff_access(self):
        view = CustomerUpdateView.as_view()
        customer_user=self.create_dummy_user(username="testcustomer",password='testpasword',email='customer@gmail.com',user_role='customer')
        data={"email":"testeemail@gmail.com"}
        request = factory.patch(f'/customer_update/{customer_user.id}/',data,format='json')  
        force_authenticate(request, user=customer_user)
        response = view(request,id=customer_user.id)
        user=User.objects.get(id=customer_user.id)
        print(user.email)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_update_non_customer(self):
        view = CustomerUpdateView.as_view()
        customer_user=self.create_dummy_user(username="testcustomer",password='testpasword',email='customer@gmail.com',user_role='staff')
        data={"email":"test@gmail.com"}
        request = factory.patch(f'/customer_update/{customer_user.id}/',data,format='json')  
        staff_user = self.create_dummy_user(username="teststaff", password='testpassword', email='staff@gmail.com', user_role='staff')
        force_authenticate(request, user=staff_user)
        response = view(request,id=customer_user.id)
        user=User.objects.get(id=customer_user.id)
        print(user.email)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    def test_not_valid_data(self):
         view=CustomerUpdateView.as_view()
         customer_user=self.create_dummy_user(username=" ",password='testpasword',email='custome.om',user_role='customer')
         data={"email":"testgmail.com"}
         request = factory.patch(f'/customer_update/{customer_user.id}/',data,format='json')  
         staff_user = self.create_dummy_user(username="teststaff", password='testpassword', email='staff@gmail.com', user_role='staff')
         force_authenticate(request, user=staff_user)
         response = view(request,id=customer_user.id)
         user=User.objects.get(id=customer_user.id)
         print(user.email)
         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class StaffUpdateViewTestCase(TestCase):
    def create_dummy_user(self,username,password,email,user_role):
            user_data={
                "username":username,
                "password":password,
                "email":email,
                "user_role":user_role
            }
            return User.objects.create_user(**user_data)
    
    def test_manager_access(self):
        view = StaffUpdateView.as_view()
        staff_user=self.create_dummy_user(username="testcustomer",password='testpasword',email='customer@gmail.com',user_role='staff')
        data={"email":"testemail@gmail.com"}
        request = factory.patch(f'staff_update/{staff_user.id}/',data,format='json')  
        manager_user = self.create_dummy_user(username="testmanager", password='testpassword', email='manager@gmail.com', user_role='manager')
        force_authenticate(request, user=manager_user)
        response = view(request,id=staff_user.id)
        user=User.objects.get(id=staff_user.id)
        print(user.email)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_manager_access(self):
        view = StaffUpdateView.as_view()
        staff_user=self.create_dummy_user(username="testcustomer",password='testpasword',email='customer@gmail.com',user_role='staff')
        data={"email":"testemail@gmail.com"}
        request = factory.patch(f'staff_update/{staff_user.id}/',data,format='json')  
        force_authenticate(request, user=staff_user)
        response = view(request,id=staff_user.id)
        user=User.objects.get(id=staff_user.id)
        print(user.email)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_update_non_staff(self):
        view =StaffUpdateView.as_view()
        staff_user=self.create_dummy_user(username="testcustomer",password='testpasword',email='customer@gmail.com',user_role='customer')
        data={"email":"test@gmail.com"}
        request = factory.patch(f'staff_update/{staff_user.id}/',data,format='json')  
        manager_user = self.create_dummy_user(username="testmanager", password='testpassword', email='manager@gmail.com', user_role='manager')
        force_authenticate(request, user=manager_user)
        response = view(request,id=staff_user.id)
        user=User.objects.get(id=staff_user.id)
        print(user.email)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_not_valid_data(self):
         view=StaffUpdateView.as_view()
         staff_user=self.create_dummy_user(username=" ",password='testpasword',email='custome.om',user_role='staff')
         data={"email":"testgmail.com"}
         request = factory.patch(f'staff_update/{staff_user.id}/',data,format='json')  
         manager_user = self.create_dummy_user(username="teststaff", password='testpassword', email='staff@gmail.com', user_role='manager')
         force_authenticate(request, user=manager_user)
         response = view(request,id=staff_user.id)
         user=User.objects.get(id=staff_user.id)
         print(user.email)
         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class AdminViewTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.manager_user = User.objects.create_user(username='manager_user', password='password', email='manager@example.com', user_role='manager')
        self.staff_user = User.objects.create_user(username='staff_user', password='password', email='staff@example.com', user_role='staff')
        self.customer_user = User.objects.create_user(username='customer_user', password='password', email='customer@example.com', user_role='customer')
    def test_admin_view_manager(self):
        request = self.factory.get('/admin/')
        request.user = self.manager_user  
        response = self.client.get('/admin/') 
        self.assertEqual(response.status_code, 302)
