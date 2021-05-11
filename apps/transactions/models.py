from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('B', 'Buy Crypto'),
        ('S', 'Sell Crypto'),
        ('T', 'Transfer Crypto'),
    )

    trade_id = models.CharField(max_length=20, default='MANUAL')
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    crypto_currency = models.CharField(max_length=10)
    crypto_amount = models.DecimalField(max_digits=24, decimal_places=10, null=True, blank=True)
    crypto_fee = models.DecimalField(max_digits=24, decimal_places=10, null=True, blank=True)
    amount_before_fee = models.DecimalField(max_digits=24, decimal_places=10)
    amount_after_fee = models.DecimalField(max_digits=24, decimal_places=10)
    exchange_rate = models.DecimalField(max_digits=24, decimal_places=10)
    fiat_currency = models.CharField(max_length=10)
    fiat_amount = models.DecimalField(max_digits=24, decimal_places=10, null=True, blank=True)
    fiat_fee = models.DecimalField(max_digits=24, decimal_places=10, null=True, blank=True)
    amount = models.DecimalField(max_digits=24, decimal_places=10)
    date_valid = models.DateTimeField('date transfered')
    transaction_type = models.CharField(max_length=1, choices=TRANSACTION_TYPES, default='B')

    class Meta:  
        db_table = "transaction"
