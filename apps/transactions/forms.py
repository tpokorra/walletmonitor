from django import forms  
import datetime
from apps.transactions.models import Transaction
from apps.rates.models import ExchangeRate
#from datetimepicker.widgets import DateTimePicker
#from django.contrib.admin.widgets import AdminDateWidget

class TransactionForm(forms.ModelForm):

    class Meta:
        model = Transaction
        fields = "__all__"  

        # https://stackoverflow.com/a/52702275/1632368
        #date_valid = forms.DateField(widget=AdminDateWidget())

        exchangerates = ExchangeRate.objects.filter(datetime_valid__gt = datetime.datetime.today() - datetime.timedelta(days=7))
        crypto_currencies = [(x, x) for x in sorted({ex.crypto_currency for ex in exchangerates})]
        fiat_currencies = [(x, x) for x in sorted({ex.fiat_currency for ex in exchangerates})]

        widgets = {
            'fiat_currency': forms.Select(choices = fiat_currencies),
            'crypto_currency': forms.Select(choices = crypto_currencies),
        }

