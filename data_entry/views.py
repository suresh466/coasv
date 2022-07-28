from django.shortcuts import render


def general_journal(request):
    template = 'data_entry/general_journal.html'

    return render(request, template)
