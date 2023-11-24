from django.db import models
from user_management.models import User
import random

def generate_account_number():
    account_number = ''.join(random.choice('0123456789') for _ in range(10))
    return account_number

class Account(models.Model):
    account_number = models.CharField(max_length=10, unique=True, default=generate_account_number)
    user= models.ForeignKey(User,on_delete=models.CASCADE, blank=True)
    account_type=models.CharField(max_length=50)
    account_balance=models.DecimalField(max_digits=10, decimal_places=2,default=0)
    joined_date=models.DateTimeField(auto_now_add=True)
    status=models.CharField(max_length=10,default='Pending')

    