from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Value
from apps.transactions.forms import TransactionForm
from apps.transactions.forms import ImportForm
from apps.transactions.models import Transaction
from apps.transactions.importbtcde import ImportBtcDe
import socket
import xlwt
from django.http import HttpResponse


@login_required
def add(request):
    if request.method == "POST":
        # request.POST is immutable, so make a copy
        values = request.POST.copy()
        values['owner'] = request.user.id
        form = TransactionForm(values)
        if form.is_valid():
            try:
                form.save()
                return redirect('/transactions/show')
            except:
                pass
    else:
        form = TransactionForm()
    return render(request,'add.html',{'form':form})

@login_required
def importbtcde(request):
    form = ImportForm()
    if request.method == "POST":
         form = ImportForm(request.POST)
         if form.is_valid():
#        try:
            importBtcDe = ImportBtcDe()
#           importBtcDe.Import(request.POST['api_key'], request.POST['api_secret'], request.POST['start_date'], request.user.id)
            importBtcDe.Import(form.cleaned_data.get('api_key'), form.cleaned_data.get('api_secret'), form.cleaned_data.get('start_date'), request.user)
            return redirect('/transactions/show')
#        except:
#            pass
    hostname = socket.gethostname()
    my_ip = socket.gethostbyname(hostname)
    return render(request,'import.html',{'form':form, 'my_ip': my_ip})

@login_required
def show(request):
    if 'crypto' in request.GET:
        transactions = Transaction.objects.filter(owner=request.user, crypto_currency=request.GET['crypto']).order_by('-date_valid').annotate(crypto_total=Value(0.0), fiat_total=Value(0.0))
    else:
        transactions = Transaction.objects.filter(owner=request.user).order_by('-date_valid').annotate(crypto_total=Value(0.0), fiat_total=Value(0.0))
    for tr in transactions:
        tr.crypto_total = 0.0
        if tr.crypto_amount:
            tr.crypto_total += float(tr.crypto_amount)
        if tr.crypto_fee:
            tr.crypto_total += float(tr.crypto_fee)
        tr.fiat_total = 0.0
        if tr.fiat_amount:
            tr.fiat_total += float(tr.fiat_amount)
        if tr.fiat_fee:
            tr.fiat_total += float(tr.fiat_fee)
    return render(request,"show.html",{'transactions':transactions})


@login_required
def export(request):
    if 'crypto' in request.GET:
        filename="transactions-"+request.GET['crypto']+".xls"
        transactions = Transaction.objects.filter(owner=request.user, crypto_currency=request.GET['crypto']).order_by('-date_valid')
    else:
        transactions = Transaction.objects.filter(owner=request.user).order_by('-date_valid')
        filename="transactions.xls"

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="'+filename+'"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Transactions')

    # header
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Date', 'Type', 'Crypto Amount', 'Crypto Fee', 'Crypto Currency', 'Fiat Amount', 'Fiat Fee', 'Fiat Currency', 'Rate', 'Description', ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # body
    font_style = xlwt.XFStyle()
    date_format = xlwt.XFStyle()
    date_format.num_format_str = 'dd/mm/yyyy'

    for row in transactions:
        row_num += 1
        ws.write(row_num, 0, row.date_valid.replace(tzinfo=None), date_format)
        ws.write(row_num, 1, row.transaction_type, font_style)
        if row.transaction_type == 'B':
            ws.write(row_num, 2, row.crypto_amount, font_style)
        elif row.crypto_amount:
            ws.write(row_num, 2, -1*row.crypto_amount, font_style)
        if row.crypto_fee:
            ws.write(row_num, 3, -1*row.crypto_fee, font_style)
        ws.write(row_num, 4, row.crypto_currency, font_style)
        if row.transaction_type == 'B' and row.fiat_amount:
            ws.write(row_num, 5, -1*row.fiat_amount, font_style)
        else:
            ws.write(row_num, 5, row.fiat_amount, font_style)
        if row.fiat_fee:
            ws.write(row_num, 6, -1*row.fiat_fee, font_style)
        ws.write(row_num, 7, row.fiat_currency, font_style)
        ws.write(row_num, 8, row.exchange_rate, font_style)
        ws.write(row_num, 9, row.description, font_style)

    wb.save(response)
    return response


@login_required
def edit(request, id):
    transaction = Transaction.objects.get(id=id, owner=request.user)
    form = TransactionForm(request.POST or None, instance = transaction)
    return render(request,'edit.html', {'transaction':transaction, 'form': form})

@login_required
def update(request, id):
    transaction = Transaction.objects.get(id=id, owner=request.user)
    # request.POST is immutable, so make a copy
    values = request.POST.copy()
    values['owner'] = request.user.id
    form = TransactionForm(values, instance = transaction)
    if form.is_valid():
        form.save()
        return redirect("/transactions/show")
    return render(request, 'edit.html', {'transaction': transaction, 'form': form})

@login_required
def destroy(request, id):
    transaction = Transaction.objects.get(id=id, owner=request.user.id)
    transaction.delete()
    return redirect("/transactions/show")
