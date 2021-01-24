from django.db import connection
import datetime
import matplotlib.pyplot as plt
from io import StringIO
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
import matplotlib.ticker as plticker
from django.http import HttpResponse

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

        loc = plticker.MultipleLocator(base=(len(x)/4.0))
        #ax.xaxis.set_major_locator(loc)

        ax.set_xlabel("time")
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

        loc = plticker.MultipleLocator(base=(len(x)/5.0))
        #ax.xaxis.set_major_locator(loc)

        ax.set_xlabel("time")
        ax.set_ylabel(Fiat)
        ax.set_title(('%s in %s' % (Crypto, Fiat)))

        response = HttpResponse(content_type = 'image/png')
        canvas = FigureCanvasAgg(fig)
        canvas.print_png(response)
        return response
