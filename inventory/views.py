from django.shortcuts import render

# Create your views here.


def sell(request):
    template = "inventory/sell.html"
    return render(request, template)
