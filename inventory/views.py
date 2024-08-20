import logging

from coasc.exceptions import (
    AccountingEquationViolationError,
    EmptyTransactionError,
    UnbalancedTransactionError,
)
from coasc.models import Ac, Decimal, Q, Split, Sum, Transaction
from django.contrib import messages as message
from django.core.exceptions import ValidationError
from django.db import transaction as db_transaction
from django.db.models.aggregates import Coalesce
from django.shortcuts import redirect, render, reverse

from inventory.forms import SaleForm
from inventory.models import Sale

# set up logging
logger = logging.getLogger(__name__)
handler = logging.FileHandler("inventory_logfile.log")
formatter = logging.Formatter(
    "%(asctime)s - %(pathname)s:%(lineno)d- %(levelname)s - %(message)s"
)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.ERROR)


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
            "quantity": quantity,
            "total_amount": item.price * quantity,
        }

        try:
            with db_transaction.atomic():
                description = f"Sale-Transaction for InventoryItem: {item.name}({item.code}), quantity {quantity} {item.unit}"
                transaction = Transaction.objects.create(desc=description)

                Sale.objects.create(**data, transaction=transaction)

                amount = data["total_amount"]
                Split.objects.create(
                    tx=transaction, t_sp="dr", ac=item.debit_account, am=amount
                )
                Split.objects.create(
                    tx=transaction, t_sp="cr", ac=item.credit_account, am=amount
                )

                item.stock -= quantity
                item.save()

                transaction.validate_transaction()
                Ac.validate_accounting_equation()
                message.success(request, description)
                return redirect(reverse("inventory:sell"))
        except EmptyTransactionError as e:
            logger.error(e)
            message.error(request, "Please make the transaction is not empty")
        except UnbalancedTransactionError as e:
            logger.error(e)
            message.error(request, "Please make sure the transaction is balanced")
        # this is redundant, for testing in dev
        except AccountingEquationViolationError as e:
            logger.error(e)
            message.error(request, "Accountion Equation is Violated")

    context = {"form": form}

    return render(request, template, context)


def transactions(request):
    template = "inventory/transactions.html"

    if request.method == "POST" and "revert" in request.POST:
        transaction_id = request.POST.get("transaction_id")
        try:
            with db_transaction.atomic():
                transaction = Transaction.objects.get(id=transaction_id)
                sale = transaction.sale
                reverted_sale = sale.revert()
                transaction.validate_transaction()
                Ac.validate_accounting_equation()
                message.success(
                    request,
                    f"Successfully reverted sale {sale.id}. New revert sale created with ID {reverted_sale.id}.",
                )
                return redirect(reverse("inventory:transactions"))
        except Transaction.DoesNotExist:
            message.error(request, f"Transaction with ID {transaction_id} not found.")
        except AttributeError:
            message.error(
                request, f"No sale associated with transaction ID {transaction_id}."
            )
        # maybe create custom exceptions later
        except ValidationError as e:
            logger.error(f"Error reverting transaction {transaction_id}: {str(e)}")
            message.warning(
                request,
                f"Error reverting transaction {transaction_id}: This sale has already been reverted.",
            )
        except Exception as e:
            logger.error(f"Error reverting transaction {transaction_id}: {str(e)}")
            message.error(
                request,
                "An error occurred while reverting the transaction. Please contact support.",
            )

    loaded_transactions = (
        Transaction.objects.filter(sale__isnull=False)
        .select_related("sale")
        .prefetch_related("split_set")
        .annotate(
            total_debit=Coalesce(
                Sum("split__am", filter=Q(split__t_sp="dr")), Decimal("0.00")
            ),
            total_credit=Coalesce(
                Sum("split__am", filter=Q(split__t_sp="cr")), Decimal("0.00")
            ),
        )
        .order_by("-tx_date", "-id")
    )

    context = {
        "transactions": loaded_transactions,
    }

    return render(request, template, context)
