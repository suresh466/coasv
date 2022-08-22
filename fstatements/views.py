from django.shortcuts import render, redirect, reverse

from coasc.models import ImpersonalAccount


def balance_sheet(request):
    template = 'fs/balance_sheet.html'

    as_acs = ImpersonalAccount.objects.filter(type_ac='AS')
    li_acs = ImpersonalAccount.objects.filter(type_ac='LI')

    if not as_acs and not li_acs:
        # later do something that makes sense
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
