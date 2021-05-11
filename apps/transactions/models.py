from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal, Context

class NonscientificDecimalField(models.DecimalField):
    """ Prevents values from being displayed with E notation, with trailing 0's
        after the decimal place  truncated. (This causes precision to be lost in
        many cases, but is more user friendly and consistent for non-scientist
        users)
    """
    def value_from_object(self, obj):
        def remove_exponent(val):
            """Remove exponent and trailing zeros.
               >>> remove_exponent(Decimal('5E+3'))
               Decimal('5000')
            """
            context = Context(prec=self.max_digits)
            return val.quantize(Decimal(1), context=context) if val == val.to_integral() else val.normalize(context)

        val = super(NonscientificDecimalField, self).value_from_object(obj)
        if isinstance(val, Decimal):
            return remove_exponent(val)

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
    crypto_amount = NonscientificDecimalField(max_digits=24, decimal_places=10, null=True, blank=True)
    crypto_fee = NonscientificDecimalField(max_digits=24, decimal_places=10, null=True, blank=True)
    exchange_rate = NonscientificDecimalField(max_digits=24, decimal_places=10)
    fiat_currency = models.CharField(max_length=10)
    fiat_amount = NonscientificDecimalField(max_digits=24, decimal_places=10, null=True, blank=True)
    fiat_fee = NonscientificDecimalField(max_digits=24, decimal_places=10, null=True, blank=True)
    date_valid = models.DateTimeField('date transfered')
    transaction_type = models.CharField(max_length=1, choices=TRANSACTION_TYPES, default='B')

    class Meta:  
        db_table = "transaction"
