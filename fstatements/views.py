from django.shortcuts import render, HttpResponse


def balance_sheet(request):
    template = 'fs/balance_sheet.html'
    return render(request, template)
