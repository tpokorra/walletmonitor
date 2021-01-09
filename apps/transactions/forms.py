from django import forms  
import datetime
from apps.transactions.models import Transaction
from apps.rates.models import ExchangeRate

class TransactionForm(forms.ModelForm):
    date_valid = forms.SplitDateTimeField(
        label="Date and Time of Transaction",
        input_time_formats=['%H:%M'],
        widget=forms.SplitDateTimeWidget(
            date_attrs={'type': 'date'},
            time_attrs={'type': 'time'},
            time_format='%H:%M'))

    class Meta:
        model = Transaction
        fields = "__all__"

        exchangerates = ExchangeRate.objects.filter(datetime_valid__gt = datetime.datetime.today() - datetime.timedelta(days=7))
        crypto_currencies = [(x, x) for x in sorted({ex.crypto_currency for ex in exchangerates})]
        fiat_currencies = [(x, x) for x in sorted({ex.fiat_currency for ex in exchangerates})]

        widgets = {
            'fiat_currency': forms.Select(choices = fiat_currencies),
            'crypto_currency': forms.Select(choices = crypto_currencies),
        }
