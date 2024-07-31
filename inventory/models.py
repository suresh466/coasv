from coasc.models import Ac
from django.db import models


class InventoryItem(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=255, unique=True)
    unit = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=11, decimal_places=2)
    stock = models.DecimalField(max_digits=12, decimal_places=3)
    # presave check for dr and cr ac not the same
    debit_account = models.ForeignKey(
        to=Ac, related_name="inventory_debit_accounts", on_delete=models.PROTECT
    )
    credit_account = models.ForeignKey(
        to=Ac, related_name="inventory_credit_accounts", on_delete=models.PROTECT
    )


class Sale(models.Model):
    item = models.ForeignKey(
        to=InventoryItem, on_delete=models.SET_NULL, blank=True, null=True
    )
    # save details even if item is modified or deleted
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    unit = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=11, decimal_places=2)
    debit_account = models.ForeignKey(
        to=Ac, related_name="sale_debits", on_delete=models.PROTECT
    )
    credit_account = models.ForeignKey(
        to=Ac, related_name="sale_credits", on_delete=models.PROTECT
    )
    total_amount = models.DecimalField(max_digits=11, decimal_places=2)
    quantity = models.DecimalField(max_digits=12, decimal_places=3)
