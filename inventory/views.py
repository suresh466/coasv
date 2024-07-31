from decimal import Decimal

from django.shortcuts import render

from inventory.forms import SaleForm
from inventory.models import Sale


def sell(request):
    template = "inventory/sell.html"

    form = SaleForm(request.POST or None)

    if form.is_valid():
        item = form.cleaned_data["item"]
        quantity = form.cleaned_data["quantity"]
        data = {
            "item": item,
            "name": item.name,
            "code": item.code,
            "unit": item.unit,
            "price": item.price,
            "debit_account": item.debit_account,
            "credit_account": item.credit_account,
            "quantity": form.cleaned_data["quantity"],
            "total_amount": item.price * quantity,
        }

        Sale.objects.create(**data)

    context = {"form": form}

    return render(request, template, context)
