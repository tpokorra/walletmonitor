from django.db import models

# Create your models here.
class ExchangeRate(models.Model):
    crypto_currency = models.CharField(max_length=10)
    fiat_currency = models.CharField(max_length=10)
    rate = models.DecimalField(max_digits=24, decimal_places=10)
    datetime_valid = models.DateTimeField('datetime valid')
    class Meta:  
        db_table = "exchangerate"

        indexes = [
            models.Index(fields=['crypto_currency', 'fiat_currency', 'datetime_valid',]),
        ]
