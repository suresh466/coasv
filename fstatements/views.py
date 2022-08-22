from django.shortcuts import render, redirect, reverse

from coasc.models import ImpersonalAccount


def trial_balance(request):
    template = 'fs/trial_balance.html'

    acs = ImpersonalAccount.objects.exclude(type_ac='')
    if not acs:
        # later do something that makes sense
        return redirect(reverse('ledgers:general_ledger'))

    cr_acs = []
    dr_acs = []
    for ac in acs:
        if ac.type_ac in ['AS', 'EX']:
            dr_acs.append(ac)
        elif ac.type_ac in ['LI', 'IN']:
            cr_acs.append(ac)

    cr_acs = [{'ac': ac, 'bal': ac.current_balance()} for ac in cr_acs]
    dr_acs = [{'ac': ac, 'bal': ac.current_balance()} for ac in dr_acs]
    total_sum = {
            'cr_acs': sum(ac['bal']['difference'] for ac in cr_acs),
            'dr_acs': sum(ac['bal']['difference'] for ac in dr_acs),
    }

    context = {
            'cr_acs': cr_acs,
            'dr_acs': dr_acs,
            'total_sum': total_sum
    }

    return render(request, template, context)


def balance_sheet(request):
    template = 'fs/balance_sheet.html'

    as_acs = ImpersonalAccount.objects.filter(type_ac='AS')
    li_acs = ImpersonalAccount.objects.filter(type_ac='LI')

    if not as_acs and not li_acs:
        return redirect(reverse('ledgers:general_ledger'))

    as_acs = [{
                'ac': ac, 'bal': ac.current_balance(),
                'children': [{
                    'ac': ca, 'bal': ca.current_balance()}
                    for ca in ac.impersonalaccount_set.all()]
    } for ac in as_acs]
    li_acs = [{
                'ac': ac, 'bal': ac.current_balance(),
                'children': [{
                    'ac': ca, 'bal': ca.current_balance()}
                    for ca in ac.impersonalaccount_set.all()]
    } for ac in li_acs]

    as_total_bal = ImpersonalAccount.total_current_balance(type_ac='AS')
    li_total_bal = ImpersonalAccount.total_current_balance(type_ac='LI')
    total_bal = {'as_bal': as_total_bal, 'li_bal': li_total_bal}
    context = {
            'as_acs': as_acs,
            'li_acs': li_acs,
            'total_bal': total_bal,
    }
    return render(request, template, context)


def income_statement(request):
    template = 'fs/income_statement.html'

    try:
        in_ac = ImpersonalAccount.objects.get(code=160)
        ex_ac = ImpersonalAccount.objects.get(code=150)
    except ImpersonalAccount.DoesNotExist:
        return redirect(reverse('ledgers:general_ledger'))

    in_ac = {
        'ac': in_ac, 'bal': in_ac.current_balance(),
        'children': [{
            'ac': ca, 'bal': ca.current_balance()}
            for ca in in_ac.impersonalaccount_set.all()]
    }
    ex_ac = {
        'ac': ex_ac, 'bal': ex_ac.current_balance(),
        'children': [{
            'ac': ca, 'bal': ca.current_balance()}
            for ca in ex_ac.impersonalaccount_set.all()]
    }

    context = {
            'in_ac': in_ac,
            'ex_ac': ex_ac,
    }

    return render(request, template, context)
