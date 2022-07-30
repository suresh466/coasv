from decimal import Decimal
from django.shortcuts import render, redirect, reverse

from coasc.models import ImpersonalAccount, Split, Transaction
from data_entry.forms import SplitForm


def general_journal(request):
    template = 'data_entry/general_journal.html'

    form = SplitForm(request.POST or None)
    if form.is_valid():
        if 'splits' not in request.session:
            request.session['splits'] = []
        account = form.cleaned_data['account']
        ac = account.pk
        ac_code = account.code
        t_s = form.cleaned_data['type_split']
        am = str(form.cleaned_data['amount'])

        split = {
                'account': ac, 'account_code': ac_code,
                'type_split': t_s, 'amount': am,
        }
        request.session['splits'].append(split)
        request.session.modified = True
        return redirect(reverse('data_entry:general_journal'))

    splits = request.session.get('splits', None)
    context = {
            'form': form,
            'splits': splits,
    }
    return render(request, template, context)


def save_transaction(request):
    splits = request.session.get('splits', None)
    if splits is None:
        raise TypeError('None is not a session split')

    desc = request.POST['description']
    tx = Transaction.objects.create(description=desc)
    for split in splits:
        ac_pk = split['account']
        ac = ImpersonalAccount.objects.get(pk=ac_pk)
        t_s = split['type_split']
        am = Decimal(split['amount'])

        Split.objects.create(
                account=ac, type_split=t_s, amount=am, transaction=tx)
    del request.session['splits']

    return redirect(reverse('data_entry:general_journal'))


def cancel_transaction(request):
    if 'splits' not in request.session:
        raise TypeError('None is not a session split')
    del request.session['splits']
    return redirect(reverse('data_entry:general_journal'))
