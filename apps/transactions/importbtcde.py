from django.db import connection
from apps.transactions.models import Transaction
from decimal import Decimal
import datetime
import btcde

class ImportBtcDe:
  def Import(self, apiKey, apiSecret, StartDate, Owner):

    conn = btcde.Connection(apiKey, apiSecret)
    page=1
    while True:
      response = conn.showMyTrades(date_start=StartDate.isoformat()+"T00:00:00+00:00", state=1,page=page)
      trades = response.get('trades')
      if not trades:
          raise Exception(('%s' % (response,)))
          raise Exception(('%s %s %s ' % (apiKey,apiSecret, StartDate.isoformat())))
          break
      for trade in trades:

        # TODO: check if this trade_id does not exist in the database for this user
        with connection.cursor() as cursor:
          sql = """SELECT trade_id FROM `transaction` WHERE trade_id=%s and owner_id=%s"""
          cursor.execute(sql, [trade['trade_id'], Owner.id])
          if cursor.rowcount > 0:
            continue

        # import the trade
        t = Transaction()
        t.trade_id = trade['trade_id']
        supported_cryptos = ['BTC', 'BCH', 'ETH']
        for c in supported_cryptos:
          if trade['trading_pair'].upper().startswith(c):
            t.crypto_currency = c
        supported_fiat = ['USD', 'EUR']
        for f in supported_fiat:
          if trade['trading_pair'].upper().endswith(f):
            t.fiat_currency = f
        t.owner = Owner
        t.amount_before_fee = Decimal(trade['amount'])
        t.amount_after_fee = Decimal(trade['amount']) - Decimal(trade['fee_currency'])
        t.amount = Decimal(trade['volume'])
        if trade['type'] == 'sell':
            t.amount -= Decimal(trade['fee_eur'])
            t.amount_before_fee *= -1
            t.amount_after_fee *= -1
            t.amount *= -1
        t.exchange_rate = trade['price']
        t.date_valid = trade['created_at']
        t.save()

      if page >= response.get('page')['last']:
        break
      page += 1

