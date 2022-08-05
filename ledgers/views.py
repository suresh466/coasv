from django.shortcuts import render

from coasc.models import ImpersonalAccount

# Create your views here.


def general_ledger(request):
    template = 'ledgers/general_ledger.html'

    accounts = ImpersonalAccount.objects.all()
    accounts_data = []
    for ac in accounts:
        ac_data = {
            'account_name': ac.name, 'account_code': ac.code,
            'splits': ac.split_set.all(), 'balances': ac.current_balance(),
        }
        accounts_data.append(ac_data)

    context = {
            'accounts_data': accounts_data,
    }
    return render(request, template, context)
