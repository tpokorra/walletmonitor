from django.db import connection
import datetime
import matplotlib.pyplot as plt
from io import StringIO
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
import matplotlib.ticker as plticker
import matplotlib.dates as mdates
from django.http import HttpResponse
from decimal import Decimal

class Graph:

    def graph_days(self, Crypto, Fiat, DayDiff):

        x = []
        y = []

        with connection.cursor() as cursor:
            sql = """SELECT datetime_valid, rate FROM
                     (select date(datetime_valid) as day, max(datetime_valid) as last
                        from exchangerate WHERE crypto_currency = %s AND fiat_currency = %s
                        AND datetime_valid >= %s
                        GROUP BY day
                        ORDER BY datetime_valid DESC) AS a
                     JOIN exchangerate AS b ON a.last = b.datetime_valid
                     AND crypto_currency = %s AND fiat_currency = %s
                     ORDER BY datetime_valid ASC"""
            startDate = datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0) - datetime.timedelta(days=int(DayDiff))
            cursor.execute(sql, [Crypto, Fiat, startDate, Crypto, Fiat])
            rows = cursor.fetchall()
            for row in rows:
                x.append(row[0])
                y.append(row[1])

        if len(x) == 0:
            raise Exception("no data for this time range in the database")

        fig_size = plt.rcParams["figure.figsize"]
        fig_size[0] = 5
        fig_size[1] = 4
        plt.rcParams["figure.figsize"] = fig_size

        fig = Figure()
        ax = fig.add_subplot(1, 1, 1)

        ax.plot(x, y, color='green', linestyle='dashed', linewidth = 2,
                 marker='o', markerfacecolor='blue', markersize=2)

        if int(DayDiff) <= 30:
            hours = mdates.DayLocator(interval = 6)
        elif int(DayDiff) <= 180:
            hours = mdates.DayLocator(interval = 30)
        elif int(DayDiff) <= 360:
            hours = mdates.DayLocator(interval = int((int(DayDiff)/6)))
        else:
            hours = mdates.DayLocator(interval = 360)

        h_fmt = mdates.DateFormatter('%b %d\n%Y')
        ax.xaxis.set_major_locator(hours)
        ax.xaxis.set_major_formatter(h_fmt)

        #ax.set_xlabel("time")
        ax.set_ylabel(Fiat)
        ax.set_title(('%s in %s' % (Crypto, Fiat)))

        response = HttpResponse(content_type = 'image/png')
        canvas = FigureCanvasAgg(fig)
        canvas.print_png(response)
        return response

    def graph_hours(self, Crypto, Fiat, HourDiff):

        x = []
        y = []

        with connection.cursor() as cursor:
            sql = """SELECT datetime_valid, rate FROM exchangerate
                     WHERE crypto_currency = %s AND fiat_currency = %s
                     AND datetime_valid >= %s
                     ORDER BY datetime_valid ASC"""
            startDate = datetime.datetime.today() - datetime.timedelta(hours=int(HourDiff))
            cursor.execute(sql, [Crypto, Fiat, startDate])
            rows = cursor.fetchall()
            for row in rows:
                x.append(row[0])
                y.append(row[1])

        if len(x) == 0:
            raise Exception("no data for this time range in the database")

        fig = Figure()
        ax = fig.add_subplot(1, 1, 1)

        ax.plot(x, y, color='green', linestyle='dashed', linewidth = 2,
                 marker='o', markerfacecolor='blue', markersize=2)

        if int(HourDiff) <= 48:
            hours = mdates.HourLocator(interval = 6)
            h_fmt = mdates.DateFormatter('%b %d\n%H:%M')
        else:
            hours = mdates.HourLocator(interval = 24)
            h_fmt = mdates.DateFormatter('%b %d\n%H:%M')

        ax.xaxis.set_major_locator(hours)
        ax.xaxis.set_major_formatter(h_fmt)

        #fig.subplots_adjust(bottom=0.2)
        #ax.set_xlabel("time")
        ax.set_ylabel(Fiat)
        ax.set_title(('%s in %s' % (Crypto, Fiat)))

        response = HttpResponse(content_type = 'image/png')
        canvas = FigureCanvasAgg(fig)
        canvas.print_png(response)
        return response

    def wallet_graph_days(self, Userid, Fiat, DayDiff):

        x = []
        y = []
        y2 = []

        with connection.cursor() as cursor:
            # first get the relevant crypto currencies
            sql = "SELECT distinct crypto_currency FROM transaction where owner_id = %s"
            cursor.execute(sql, [Userid,])
            currency_rows = cursor.fetchall()
            cryptos = []
            for currency_row in currency_rows:
                cryptos.append(currency_row[0])

            # loop through the days
            start_date = datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0) - datetime.timedelta(days=int(DayDiff))
            end_date = datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
            delta = datetime.timedelta(days=1)

            while start_date <= end_date:
                date = start_date
                start_date += delta

                total_fiat_amount = Decimal(0)
                total_fiat_value = Decimal(0)

                # get the average exchange rates for this day
                sql = """SELECT AVG(rate), crypto_currency
                         FROM exchangerate
                         WHERE fiat_currency = %s
                         AND crypto_currency IN %s
                         AND datetime_valid BETWEEN %s AND %s
                         GROUP BY crypto_currency"""
                cursor.execute(sql, [Fiat, cryptos, date, date + delta])
                rate_rows = cursor.fetchall()

                # get the current amount on that day
                sql = """SELECT crypto_currency, transaction_type, SUM(crypto_amount), SUM(fiat_amount), SUM(crypto_fee), SUM(fiat_fee)
                         FROM transaction
                         WHERE owner_id = %s
                         AND date_valid <= %s
                         GROUP BY crypto_currency, transaction_type"""
                cursor.execute(sql, [Userid, date])
                amount_rows = cursor.fetchall()

                for rate_row in rate_rows:
                    rate = rate_row[0]
                    crypto = rate_row[1]
                    total_crypto_amount = Decimal(0)

                    for amount_row in amount_rows:
                        tr_crypto = amount_row[0]
                        if tr_crypto == crypto:
                           tr_type = amount_row[1]
                           tr_amount = amount_row[2]
                           tr_fiat_amount = amount_row[3]
                           tr_crypto_fee = amount_row[4]
                           tr_fiat_fee = amount_row[5]
                           if tr_amount:
                               if tr_type == "S":
                                   total_crypto_amount -= tr_amount
                                   total_fiat_amount += tr_fiat_amount
                               elif tr_type == "B":
                                   total_crypto_amount += tr_amount
                                   total_fiat_amount -= tr_fiat_amount
                           if tr_crypto_fee:
                                total_crypto_amount -= tr_crypto_fee
                           if tr_fiat_fee:
                                total_fiat_value -= tr_fiat_fee
                                total_fiat_amount -= tr_fiat_fee
                    total_fiat_value += total_crypto_amount * rate

                x.append(date)
                y.append(total_fiat_value)
                y2.append(total_fiat_amount)


        if len(x) == 0:
            raise Exception("no data for this time range in the database")

        fig_size = plt.rcParams["figure.figsize"]
        fig_size[0] = 5
        fig_size[1] = 4
        plt.rcParams["figure.figsize"] = fig_size

        fig = Figure()
        ax = fig.add_subplot(1, 1, 1)

        ax.plot(x, y, color='green', linestyle='dashed', linewidth = 2,
                 marker='o', markerfacecolor='blue', markersize=2)
        ax.plot(x, y2, color='blue', linestyle='dashed', linewidth = 2,
                 marker='o', markerfacecolor='red', markersize=2)

        if int(DayDiff) <= 30:
            hours = mdates.DayLocator(interval = 6)
        elif int(DayDiff) <= 180:
            hours = mdates.DayLocator(interval = 30)
        elif int(DayDiff) <= 360:
            hours = mdates.DayLocator(interval = int((int(DayDiff)/6)))
        else:
            hours = mdates.DayLocator(interval = 360)

        h_fmt = mdates.DateFormatter('%b %d\n%Y')
        ax.xaxis.set_major_locator(hours)
        ax.xaxis.set_major_formatter(h_fmt)

        #ax.set_xlabel("time")
        ax.set_ylabel(Fiat)
        Crypto = "Wallet"
        ax.set_title(('%s in %s' % (Crypto, Fiat)))

        response = HttpResponse(content_type = 'image/png')
        canvas = FigureCanvasAgg(fig)
        canvas.print_png(response)
        return response
