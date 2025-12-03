from django.db import connection
from apps.transactions.models import Transaction
from apps.rates.models import ExchangeRate
from decimal import Decimal
import datetime
from django.utils import timezone

class Calc:
  def ShowDiffRate(self, DayDiff, CurrentRate, Crypto, Fiat):
    with connection.cursor() as cursor:
        sql = """SELECT rate, datetime_valid FROM exchangerate WHERE crypto_currency = %s AND fiat_currency = %s
           AND datetime_valid BETWEEN %s AND %s
           ORDER BY datetime_valid DESC"""
        startDate = datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0) - datetime.timedelta(days=int(DayDiff))
        endDate = startDate + datetime.timedelta(days=1)
        cursor.execute(sql, [Crypto, Fiat, startDate, endDate])
        rateMinusXDay = cursor.fetchone()
        if rateMinusXDay and Decimal(rateMinusXDay[0]) > 0:
            return {"dateRelative": "%s days ago" % (DayDiff,), "date" : rateMinusXDay[1], "rateEUR": rateMinusXDay[0],
                "diffPercentage": (CurrentRate.rate-Decimal(rateMinusXDay[0]))/Decimal(rateMinusXDay[0])*100, "rateUSD": None}
    return None

  def CalcHistory(self, Hours, Crypto, Fiat):
    with connection.cursor() as cursor:
        startDate = datetime.datetime.today() - datetime.timedelta(hours=Hours)
        endDate = datetime.datetime.today()
        sql = """SELECT datetime_valid, rate FROM exchangerate
                  WHERE crypto_currency = %s AND fiat_currency = %s
                  AND datetime_valid BETWEEN %s AND %s
                  ORDER BY datetime_valid ASC LIMIT 1"""
        cursor.execute(sql, [Crypto, Fiat, startDate, endDate])
        startRate = cursor.fetchone()
        if not startRate:
            return {}
        sql = """SELECT datetime_valid, rate FROM exchangerate
                  WHERE crypto_currency = %s AND fiat_currency = %s
                  AND datetime_valid BETWEEN %s AND %s
                  ORDER BY datetime_valid DESC LIMIT 1"""
        cursor.execute(sql, [Crypto, Fiat, startDate, endDate])
        endRate = cursor.fetchone()
        sql = """SELECT datetime_valid, rate FROM exchangerate
                  WHERE crypto_currency = %s AND fiat_currency = %s
                  AND datetime_valid BETWEEN %s AND %s
                  ORDER BY rate DESC LIMIT 1"""
        cursor.execute(sql, [Crypto, Fiat, startDate, endDate])
        maxRate = cursor.fetchone()
        sql = """SELECT datetime_valid, rate FROM exchangerate
                  WHERE crypto_currency = %s AND fiat_currency = %s
                  AND datetime_valid BETWEEN %s AND %s
                  ORDER BY rate ASC LIMIT 1"""
        cursor.execute(sql, [Crypto, Fiat, startDate, endDate])
        minRate = cursor.fetchone()
        diffPercentage = -1
        if startRate[1] > 0:
            diffPercentage = (Decimal(endRate[1])-Decimal(startRate[1]))/Decimal(startRate[1])*100
        return {"startdate": startRate[0], "startvalue": startRate[1],
                "curdate": endRate[0], "curvalue": endRate[1],
                "mindate": minRate[0], "minvalue": minRate[1],
                "maxdate": maxRate[0], "maxvalue": maxRate[1],
                "diffPercentage": diffPercentage}
    return None


  def GetCurrentValue(self, userid, crypto, total_investment, current_value, total_tax_free):
    amount_kept = 0
    last_updated = None
    out = {}
    out["crypto"] = crypto

    with connection.cursor() as cursor:
        sql = """SELECT SUM(crypto_amount) as crypto_amount, SUM(fiat_amount) as fiat_amount FROM `transaction` WHERE transaction_type = 'B' and crypto_currency=%s and owner_id=%s"""
        cursor.execute(sql, [crypto, userid])
        bought = cursor.fetchone()
        if bought[0]:
          out["bought"] = bought[1]
          total_investment += Decimal(bought[1])
          amount_kept += Decimal(bought[0])
        else:
          out["bought"] = None
    
    with connection.cursor() as cursor:
        sql = """SELECT SUM(crypto_amount) as crypto_amount, SUM(fiat_amount) as fiat_amount FROM `transaction` WHERE transaction_type = 'S' and crypto_currency=%s and owner_id=%s"""
        cursor.execute(sql, [crypto, userid])
        sold = cursor.fetchone()
        if sold[0]:
          out["sold"] = sold[1]
          total_investment -= Decimal(sold[1])
          amount_kept -= Decimal(sold[0])
        else:
          out["sold"] = None

    # calculate all fees.
    with connection.cursor() as cursor:
        sql = """SELECT SUM(crypto_fee) as crypto_fee, SUM(fiat_fee) as fiat_fee FROM `transaction` WHERE crypto_currency=%s and owner_id=%s"""
        cursor.execute(sql, [crypto, userid])
        fees = cursor.fetchone()
        if fees[1]:
          total_investment -= Decimal(fees[1])
        if fees[0]:
          amount_kept -= Decimal(fees[0])

    rateEUR = ExchangeRate.objects.filter(crypto_currency=crypto, fiat_currency='EUR').order_by('-datetime_valid').first()
    rateUSD = ExchangeRate.objects.filter(crypto_currency=crypto, fiat_currency='USD').order_by('-datetime_valid').first()

    if rateEUR:
      cv =  Decimal(rateEUR.rate) * amount_kept
      current_value += cv
      out["current_value"] = cv
      out["amount_kept"] = amount_kept
      out["rateEUR"] = rateEUR.rate
      last_updated = rateEUR.datetime_valid
    else:
      out["current_value"] = None
      out["amount_kept"] = None
      out["rateEUR"] = None

    out["rates"] = []
    if rateUSD and rateEUR:
        out["rates"].append({"dateRelative": "Now", "date" : rateEUR.datetime_valid, "rateEUR": rateEUR.rate, "diffPercentage": None, "rateUSD": rateUSD.rate})

    if rateEUR:
      for daydiff in ["1", "3", "7", "14", "30"]:
        diffrate = self.ShowDiffRate(daydiff, rateEUR, crypto, 'EUR')
        if diffrate:
          out["rates"].append(diffrate)

    out["graphs"] = []
    out["graphs"].append({"id": "h48", "active": "active", "label": "48 hours", "period": "number_of_hours=48", **self.CalcHistory(24*2, crypto, 'EUR')})
    out["graphs"].append({"id": "d3", "label": "3 days", "period": "number_of_hours=72", **self.CalcHistory(24*3, crypto, 'EUR')})
    out["graphs"].append({"id": "w1", "label": "1 week", "period": "number_of_hours=168", **self.CalcHistory(24*7, crypto, 'EUR')})
    out["graphs"].append({"id": "m1", "label": "1 month", "period": "number_of_days=30", **self.CalcHistory(24*30, crypto, 'EUR')})
    out["graphs"].append({"id": "m6", "label": "6 months", "period": "number_of_days=180", **self.CalcHistory(24*180, crypto, 'EUR')})
    out["graphs"].append({"id": "y1", "label": "1 year", "period": "number_of_days=360", **self.CalcHistory(24*360, crypto, 'EUR')})
    out["graphs"].append({"id": "y10", "label": "10 years", "period": "number_of_days=3600", **self.CalcHistory(24*3600, crypto, 'EUR')})

    amount_within_past_year = 0
    with connection.cursor() as cursor:
        sql = """SELECT SUM(crypto_amount) as amount FROM `transaction` WHERE transaction_type='B' and crypto_currency=%s and owner_id=%s and date_valid>%s"""
        date_valid = timezone.make_aware(datetime.datetime.now() - datetime.timedelta(days=365), timezone=timezone.get_current_timezone())
        cursor.execute(sql, [crypto, userid, date_valid])
        bought = cursor.fetchone()
        out["bought_recently"] = None
        if bought[0]:
          out["bought_recently"] = bought[0]
          amount_within_past_year = Decimal(bought[0])
        if amount_kept > amount_within_past_year:
          amount_available_to_sell = amount_kept - amount_within_past_year
        else:
          amount_available_to_sell = 0
        out["bought_tax_free"] = None
        out["value_tax_free"] = None
        out["avg_price_tax_free"] = None
        if rateEUR:
          out["bought_tax_free"] = amount_available_to_sell
          out["value_tax_free"] = amount_available_to_sell * rateEUR.rate
          total_tax_free += out["value_tax_free"]


    # A: 4 gekauft zum Preis von 5
    # B: 3 verkauft
    # C: 2 gekauft zum Preis von 7
    # D: 2 verkauft
    # E: 5 gekauft zum Preis von 10.
    # Durchschnitts-Einkaufspreis: (1*7 + 5*10) / (1+5) = 9.5
    with connection.cursor() as cursor:
        tx = []
        sql = """SELECT crypto_amount, crypto_fee, exchange_rate, transaction_type, date_valid FROM `transaction` WHERE crypto_currency=%s and owner_id=%s and (date_valid<=%s OR transaction_type <> 'B') ORDER BY date_valid ASC"""
        date_valid = timezone.make_aware(datetime.datetime.now() - datetime.timedelta(days=365), timezone=timezone.get_current_timezone())
        cursor.execute(sql, [crypto, userid, date_valid])
        records = cursor.fetchall()
        for row in records:
            if row[3] == 'B':
                amount = row[0]
                if row[1] is not None:
                    amount -= row[1]
                tx.append([amount, row[2], row[3], row[4]])
            elif row[3] in ('S','T'):
                sold = 0
                if row[0] is not None:
                    sold += row[0]
                if row[1] is not None:
                    sold += row[1]
                for b in tx:
                    if b[0] > 0 and sold > 0:
                        print("  ", b)
                        if sold <= b[0]:
                          b[0] -= sold
                          sold = 0
                        if sold > b[0]:
                          sold -= b[0]
                          b[0] = 0
        total_fiat = 0
        total_crypto = 0
        for b in tx:
            total_crypto += b[0]
            total_fiat += b[0]*b[1]
        if total_fiat != 0:
            out["avg_price_tax_free"] = round(total_fiat / total_crypto, 2)

    return (total_investment, current_value, total_tax_free, rateEUR.rate, rateUSD.rate, last_updated, out)

  def GetWalletGraphs(self, userid):
    out = {}
    out["graphs"] = []
    out["graphs"].append({"id": "w1", "label": "1 week", "period": "number_of_days=7"})
    out["graphs"].append({"id": "m1", "active": "active", "label": "1 month", "period": "number_of_days=30"})
    out["graphs"].append({"id": "m6", "label": "6 months", "period": "number_of_days=180"})
    out["graphs"].append({"id": "y1", "label": "1 year", "period": "number_of_days=365"})
    out["graphs"].append({"id": "y3", "label": "3 years", "period": "number_of_days=" + str(365*3)})
    out["graphs"].append({"id": "y5", "label": "5 years", "period": "number_of_days=" + str(365*5)})
    out["graphs"].append({"id": "y10", "label": "10 years", "period": "number_of_days=" + str(365*10)})

    return (out["graphs"])
