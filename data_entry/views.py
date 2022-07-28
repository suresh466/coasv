from django.shortcuts import render, redirect, reverse

from data_entry.forms import SplitForm


def general_journal(request):
    template = 'data_entry/general_journal.html'
    form = SplitForm(request.POST or None)

    if form.is_valid():
        if 'splits' not in request.session:
            request.session['splits'] = []
        ac = request.POST['account']
        t_s = request.POST['type_split']
        am = request.POST['amount']
        split = {'account': ac, 'type_split': t_s, 'amount': am}
        request.session['splits'].append(split)
        return redirect(reverse('data_entry:general_journal'))

    splits = request.session.get('splits', None)
    context = {
            'form': form,
            'splits': splits,
    }

    return render(request, template, context)
