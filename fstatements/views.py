from django.shortcuts import render, redirect, reverse

from coasc.models import ImpersonalAc


def trial_balance(request):
    template = 'fs/trial_balance.html'

    acs = ImpersonalAc.objects.exclude(t_ac='')
    if not acs:
        # later do something that makes sense
        return redirect(reverse('ledgers:general_ledger'))

    cr_acs = []
    dr_acs = []

    for ac in acs:
        if ac.t_ac in ['AS', 'EX']:
            dr_acs.append(ac)
        elif ac.t_ac in ['LI', 'IN']:
            cr_acs.append(ac)

    cr_acs = [{'ac': ac, 'bal': ac.bal()} for ac in cr_acs]
    dr_acs = [{'ac': ac, 'bal': ac.bal()} for ac in dr_acs]

    total_sum = {
            'cr_acs': sum(ac['bal']['diff'] for ac in cr_acs),
            'dr_acs': sum(ac['bal']['diff'] for ac in dr_acs),
    }

    context = {
            'cr_acs': cr_acs,
            'dr_acs': dr_acs,
            'total_sum': total_sum
    }

    return render(request, template, context)


def balance_sheet(request):
    template = 'fs/balance_sheet.html'

    li_acs = ImpersonalAc.objects.filter(t_ac='LI')
    as_acs = ImpersonalAc.objects.filter(t_ac='AS')

    if not li_acs and not as_acs:
        return redirect(reverse('ledgers:general_ledger'))

    li_acs = [{
                'ac': ac, 'bal': ac.bal(),
                'children': [{
                    'ac': ca, 'bal': ca.bal()}
                    for ca in ac.impersonalac_set.all()]
    } for ac in li_acs]

    as_acs = [{
                'ac': ac, 'bal': ac.bal(),
                'children': [{
                    'ac': ca, 'bal': ca.bal()}
                    for ca in ac.impersonalac_set.all()]
    } for ac in as_acs]

    li_total_bal = ImpersonalAc.total_bal(t_ac='LI')
    as_total_bal = ImpersonalAc.total_bal(t_ac='AS')

    context = {
            'li_acs': li_acs,
            'as_acs': as_acs,
            'li_total_bal': li_total_bal,
            'as_total_bal': as_total_bal,
    }
    return render(request, template, context)


def income_statement(request):
    template = 'fs/income_statement.html'

    try:
        in_ac = ImpersonalAc.objects.get(code=160)
        ex_ac = ImpersonalAc.objects.get(code=150)
    except ImpersonalAc.DoesNotExist:
        return redirect(reverse('ledgers:general_ledger'))

    in_ac = {
        'ac': in_ac, 'bal': in_ac.bal(),
        'children': [{
            'ac': ca, 'bal': ca.bal()}
            for ca in in_ac.impersonalac_set.all()]
    }

    ex_ac = {
        'ac': ex_ac, 'bal': ex_ac.bal(),
        'children': [{
            'ac': ca, 'bal': ca.bal()}
            for ca in ex_ac.impersonalac_set.all()]
    }

    context = {
            'in_ac': in_ac,
            'ex_ac': ex_ac,
    }

    return render(request, template, context)
