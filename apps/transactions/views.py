from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.transactions.forms import TransactionForm
from apps.transactions.models import Transaction

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
def show(request):
    if 'crypto' in request.GET:
        transactions = Transaction.objects.filter(owner=request.user, crypto_currency=request.GET['crypto']).order_by('-date_valid')
    else:
        transactions = Transaction.objects.filter(owner=request.user).order_by('-date_valid')
    return render(request,"show.html",{'transactions':transactions})

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
