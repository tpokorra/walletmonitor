from django import forms  
from apps.transactions.models import Transaction
#from datetimepicker.widgets import DateTimePicker
#from django.contrib.admin.widgets import AdminDateWidget

class TransactionForm(forms.ModelForm):

    class Meta:
        model = Transaction
        fields = "__all__"  

        # https://stackoverflow.com/a/52702275/1632368
        #date_valid = forms.DateField(widget=AdminDateWidget())

