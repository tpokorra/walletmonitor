from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
import pytz
from apps.transactions.models import Transaction
from apps.rates.models import ExchangeRate
from apps.monitor.calc import Calc
from apps.monitor.graph import Graph

@login_required
def monitor(request):
    transactions = Transaction.objects.filter(owner=request.user)
    crypto_currencies = sorted({tr.crypto_currency for tr in transactions})
    cryptos = []
    total_investment = 0
    current_value = 0
    total_tax_free = 0
    last_updated = None
    calc = Calc()

    for crypto in crypto_currencies:
        (total_investment, current_value, total_tax_free, rateEUR, rateUSD, last_updated, out2) = calc.GetCurrentValue(request.user.id, crypto, total_investment, current_value, total_tax_free)

        cryptos.append({"crypto": crypto, "rateEUR": rateEUR, "rateUSD": rateUSD, **out2})

    django_timezone = pytz.timezone(settings.TIME_ZONE)

    return render(request,"monitor.html",
            {'cryptos':cryptos,
                'total_tax_free': total_tax_free,
                'total_investment': total_investment,
                'current_value': current_value,
                'last_updated': last_updated,
                'django_timezone': django_timezone})

@login_required
def graph(request):
    if not 'crypto' in request.GET:
        return
    if not 'fiat' in request.GET:
        return
    Crypto = request.GET['crypto']
    Fiat = request.GET['fiat']

    if 'number_of_days' in request.GET:
        return Graph().graph_days(Crypto, Fiat, request.GET['number_of_days'])
    if 'number_of_hours' in request.GET:
        return Graph().graph_hours(Crypto, Fiat, request.GET['number_of_hours'])
