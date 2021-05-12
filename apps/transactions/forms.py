from django import forms  
import sys
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

        # do not run this code in initial migration, because the database has not been built yet
        if not "migrate" in sys.argv:
            exchangerates = ExchangeRate.objects.filter(datetime_valid__gt = datetime.datetime.today() - datetime.timedelta(days=7))
            crypto_currencies = [(x, x) for x in sorted({ex.crypto_currency for ex in exchangerates})]
            fiat_currencies = [(x, x) for x in sorted({ex.fiat_currency for ex in exchangerates})]

            widgets = {
                'fiat_currency': forms.Select(choices = fiat_currencies),
                'crypto_currency': forms.Select(choices = crypto_currencies),
            }

class ImportForm(forms.Form):
    api_key = forms.CharField(label='API Key', widget=forms.PasswordInput, max_length=100)
    api_secret = forms.CharField(label='API Secret', widget=forms.PasswordInput, max_length=100)
    YEAR_CHOICES = []
    now = datetime.datetime.now()
    for y in range(2000,now.year+1):
      YEAR_CHOICES.append(y)
    start_date = forms.DateField(label='Start Date', widget=forms.SelectDateWidget(years=YEAR_CHOICES), initial=datetime.datetime(year=now.year, month=1, day=1))
