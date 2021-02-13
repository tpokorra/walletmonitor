from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Transaction(models.Model):
    trade_id = models.CharField(max_length=20, default='MANUAL')
    crypto_currency = models.CharField(max_length=10)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    amount_before_fee = models.DecimalField(max_digits=24, decimal_places=10)
    amount_after_fee = models.DecimalField(max_digits=24, decimal_places=10)
    exchange_rate = models.DecimalField(max_digits=24, decimal_places=10)
    fiat_currency = models.CharField(max_length=10)
    amount = models.DecimalField(max_digits=24, decimal_places=10)
    date_valid = models.DateTimeField('date transfered')
    class Meta:  
        db_table = "transaction"
