from decimal import Decimal

from coasc.models import Ac, Transaction
from django.core.exceptions import ValidationError
from django.db import models
from django.db import transaction as db_transaction


class InventoryItem(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=255, unique=True)
    unit = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    stock = models.DecimalField(max_digits=12, decimal_places=3)
    # presave check for dr and cr ac not the same
    debit_account = models.ForeignKey(
        to=Ac, related_name="inventory_debit_accounts", on_delete=models.PROTECT
    )
    credit_account = models.ForeignKey(
        to=Ac, related_name="inventory_credit_accounts", on_delete=models.PROTECT
    )

    def __str__(self):
        string = f"{self.name} ({self.code})"
        return string


class Sale(models.Model):
    item = models.ForeignKey(
        to=InventoryItem, on_delete=models.SET_NULL, blank=True, null=True
    )
    # save details in case item is deleted
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    unit = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    debit_account = models.ForeignKey(
        to=Ac, related_name="sale_debits", on_delete=models.PROTECT
    )
    credit_account = models.ForeignKey(
        to=Ac, related_name="sale_credits", on_delete=models.PROTECT
    )
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    quantity = models.DecimalField(max_digits=12, decimal_places=3)
    transaction = models.OneToOneField(
        to=Transaction, on_delete=models.SET_NULL, null=True
    )
    original_sale = models.OneToOneField(
        to="self",
        on_delete=models.SET_NULL,
        null=True,
        related_name="revert_sale",
        editable=False,
        default=None,
    )
    stock_increased = models.BooleanField(default=False)
    # each sale transaction can only be reverted once. (But the revert sale can be reverted again)
    is_reverted = models.BooleanField(default=False)

    def clean(self):
        if self.quantity < 0:
            raise ValidationError("Quantity cannot be negative")

    def get_stock_effect(self):
        """
        Calculate the net effect on stock.
        Positive value means stock increase, negative value means stock decrease.
        """
        return -Decimal(str(self.quantity)) if self.stock_increased else self.quantity

    def revert(self):
        if self.is_reverted:
            raise ValidationError("This sale has already been reverted.")

        with db_transaction.atomic():
            revert_transaction = self.transaction.revert_transaction()

            # Create revert sale
            revert_sale = Sale.objects.create(
                item=self.item,
                name=self.name,
                code=self.code,
                unit=self.unit,
                transaction=revert_transaction,
                quantity=self.quantity,
                price=self.price,
                total_amount=-Decimal(str(self.total_amount)),  # Negative for revert
                stock_increased=not self.stock_increased,  # Opposite effect on stock in case revert sale is reverted
                original_sale=self,
                debit_account=self.credit_account,
                credit_account=self.debit_account,
            )

            # Update inventory
            self.item.stock += self.get_stock_effect()
            self.item.save()

            self.is_reverted = True
            self.save()

        return revert_sale

    def __str__(self):
        effect = "increased" if self.stock_increased else "decreased"
        return f"Sale {self.id}: stock {effect} by {self.quantity} {self.item.unit}s of {self.item.name}"
