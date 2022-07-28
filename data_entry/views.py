from django.shortcuts import render, redirect, reverse

from coasc.models import Transaction

from data_entry.forms import SplitForm


def general_journal(request):
    template = 'data_entry/general_journal.html'

    form = SplitForm(request.POST or None)
    if form.is_valid():
        transaction = Transaction.objects.create(description='description1')
        form.instance.transaction = transaction
        form.save()
        return redirect(reverse('data_entry:general_journal'))

    context = {
            'form': form,
    }

    return render(request, template, context)
