from django.db import models
from django.contrib.auth.models import AbstractUser

customer="customer"
manager="manager"
staff="staff"
user_role_choices=(
        ("customer","customer"),
        ("manager","manager"),
        ("staff","staff"),

)
class User(AbstractUser):
    user_role=models.CharField(max_length=8,choices= user_role_choices)
   
  

