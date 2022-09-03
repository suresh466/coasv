from decimal import Decimal
from django.shortcuts import render, redirect, reverse
from django.db import transaction as db_transaction

from coasc.models import Ac, Split, Transaction
from data_entry.forms import SplitForm


def session_balances(splits):
    dr_sum = Decimal(0)
    cr_sum = Decimal(0)
    diff = Decimal(0)

    if splits is None:
        return {'dr_sum': dr_sum, 'cr_sum': cr_sum, 'diff': diff}

    for sp in splits:
        sp_am = Decimal(sp['am'])

        if sp['t_sp'] == 'dr':
            dr_sum += sp_am
            continue
        else:
            cr_sum += sp_am

    diff = dr_sum - cr_sum
    return {'dr_sum': dr_sum, 'cr_sum': cr_sum, 'diff': diff}


def general_journal(request):
    template = 'data_entry/general_journal.html'

    form = SplitForm(request.POST or None)

    if form.is_valid():
        if 'splits' not in request.session:
            request.session['splits'] = []

        ac = form.cleaned_data['ac']
        ac_pk = ac.pk
        ac_code = ac.code

        t_sp = form.cleaned_data['t_sp']
        am = str(form.cleaned_data['am'])

        split = {'ac': ac_pk, 'ac_code': ac_code, 't_sp': t_sp, 'am': am}
        request.session['splits'].append(split)
        request.session.modified = True

        return redirect(reverse('data_entry:general_journal'))

    splits = request.session.get('splits', None)
    session_bals = session_balances(splits)

    context = {
            'form': form,
            'splits': splits,
            'session_bals': session_bals,
    }

    return render(request, template, context)


def save_transaction(request):
    splits = request.session.get('splits', None)
    if splits is None:
        raise TypeError('None is not a session split')

    desc = request.POST['desc']
    with db_transaction.atomic():
        tx = Transaction.objects.create(desc=desc)

        for sp in splits:
            ac_pk = sp['ac']
            ac = Ac.objects.get(pk=ac_pk)

            t_sp = sp['t_sp']
            am = Decimal(sp['am'])
            Split.objects.create(ac=ac, t_sp=t_sp, am=am, tx=tx)

        Ac.validate_accounting_equation()

    del request.session['splits']

    return redirect(reverse('data_entry:general_journal'))


def cancel_transaction(request):
    if 'splits' not in request.session:
        raise TypeError('None is not a session split')
    del request.session['splits']

    return redirect(reverse('data_entry:general_journal'))
