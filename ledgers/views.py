from django.shortcuts import render

# Create your views here.


def general_ledger(request):
    template = 'ledgers/general_ledger.html'
    return render(request, template)
