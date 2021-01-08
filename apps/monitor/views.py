from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.transactions.models import Transaction
from apps.rates.models import ExchangeRate
from apps.monitor.calc import Calc

@login_required
def monitor(request):
    transactions = Transaction.objects.filter(owner=request.user)
    crypto_currencies = sorted({tr.crypto_currency for tr in transactions})
    cryptos = []
    total_investment = 0
    current_value = 0
    total_tax_free = 0
    calc = Calc()

    for crypto in crypto_currencies:
        (total_investment, current_value, total_tax_free, rateEUR, rateUSD, out2) = calc.GetCurrentValue(request.user.id, crypto, total_investment, current_value, total_tax_free)

        cryptos.append({"crypto": crypto, "rateEUR": rateEUR, "rateUSD": rateUSD, **out2})

    return render(request,"monitor.html",{'cryptos':cryptos})
