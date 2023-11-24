from rest_framework import serializers
from .models import Transaction
from account_management.serializers import AccountSerializer

class TransactionSerializer(serializers.ModelSerializer):
    account=AccountSerializer
    class Meta:
        model = Transaction
        fields ='__all__'