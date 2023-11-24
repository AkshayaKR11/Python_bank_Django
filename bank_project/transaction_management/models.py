from django.db import models
from django.db import models
from account_management.models import Account
deposit="deposit"
withdraw="withdraw"
transaction_choices=[
        ("deposit","deposit"),
        ("withdraw","withdraw"),
    ]
class Transaction(models.Model):
  
    transaction_type=models.CharField(max_length=8,choices= transaction_choices,default=deposit)
    transaction_amount=models.DecimalField(max_digits=10, decimal_places=2)
    transaction_date=models.DateTimeField(auto_now_add=True)
    account= models.ForeignKey(Account,on_delete=models.CASCADE, blank=True)
    