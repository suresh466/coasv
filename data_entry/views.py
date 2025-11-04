import logging
import uuid
from decimal import Decimal

import django.forms as forms
from coasc.exceptions import AccountingEquationViolationError
from coasc.models import Ac, Split, Transaction
from django.contrib import messages as message
from django.db import transaction as db_transaction
from django.db.models import Q, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import redirect, render, reverse

from data_entry.forms import SplitForm, TransactionForm

# set up logging
logger = logging.getLogger(__name__)
handler = logging.FileHandler("data_entry_logfile.log")
formatter = logging.Formatter(
    "%(asctime)s - %(pathname)s:%(lineno)d- %(levelname)s - %(message)s"
)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.ERROR)


# move it to apropriate file later
class NoSplitsError(TypeError):
    """Raised when no splits are found in the session."""

    pass


def session_balances(splits):
    dr_sum = Decimal(0)
    cr_sum = Decimal(0)
    diff = Decimal(0)

    if splits is None:
        return {"dr_sum": dr_sum, "cr_sum": cr_sum, "diff": diff}
    for sp in splits:
        sp_am = Decimal(sp["am"])

        if sp["t_sp"] == "dr":
            dr_sum += sp_am
            continue
        else:
            cr_sum += sp_am

    diff = dr_sum - cr_sum
    return {"dr_sum": dr_sum, "cr_sum": cr_sum, "diff": diff}


def general_journal(request):
    template = "data_entry/general_journal.html"

    # bind post data to the relevant form
    split_form = SplitForm(
        request.POST if "add_split" in request.POST else None, prefix="split"
    )
    transaction_form = TransactionForm(
        request.POST if "save_transaction" in request.POST else None,
        prefix="transaction",
    )

    if "splits" not in request.session:
        request.session["splits"] = []
    splits = request.session.get("splits")

    if request.method == "POST":
        if "add_split" in request.POST and split_form.is_valid():
            sp_id = str(uuid.uuid4())
            ac = split_form.cleaned_data["ac"]
            ac_pk = ac.pk
            ac_code = ac.code
            ac_name = ac.name

            t_sp = split_form.cleaned_data["t_sp"]
            am = str(split_form.cleaned_data["am"])

            split = {
                "sp_id": sp_id,
                "ac": ac_pk,
                "ac_code": ac_code,
                "ac_name": ac_name,
                "t_sp": t_sp,
                "am": am,
            }
            splits.append(split)
            request.session.modified = True

            message.success(
                request,
                f"Split successfully added: {ac_name} ({ac_code}) | {t_sp}: {am}",
            )
            return redirect(reverse("data_entry:general_journal"))

        elif "save_transaction" in request.POST and transaction_form.is_valid():
            try:
                # if splits is empty assign None to it; None is not iterable so avoid empty transaction if not caught somehow
                splits = request.session.get("splits") or None
                if not splits:
                    raise NoSplitsError

                with db_transaction.atomic():
                    tx = transaction_form.save()

                    for sp in splits:
                        ac_pk = sp["ac"]
                        ac = Ac.objects.get(pk=ac_pk)

                        t_sp = sp["t_sp"]
                        am = Decimal(sp["am"])
                        Split.objects.create(ac=ac, t_sp=t_sp, am=am, tx=tx)

                    # maybe validate just the current transaction later
                    Ac.validate_accounting_equation()
                    request.session["splits"] = []
                    message.success(
                        request, f"Transaction successfully saved: {tx.desc}"
                    )
                    return redirect(reverse("data_entry:general_journal"))
            except AccountingEquationViolationError as e:
                logger.error(e)
                message.error(request, "Please make sure Debit and Credit are balanced")
            except NoSplitsError as e:
                logger.error(e)
                message.warning(request, "Please check if you have any splits!")
            except Exception as e:
                logger.error(e)
                message.error(request, "An error occurred while saving the transaction")

        elif "delete_split" in request.POST:
            sp_id = request.POST.get("sp_id")
            for sp in splits:
                if sp["sp_id"] == sp_id:
                    splits.remove(sp)
                    request.session.modified = True
                    message.warning(
                        request,
                        f"Split deleted successfully: {sp['ac_name']} ({sp['ac_code']}) | {sp['t_sp']}: {sp['am']}",
                    )
                    return redirect(reverse("data_entry:general_journal"))

            message.error(request, "Split with id: {sp_id} not found, deletion failed")
            return redirect(reverse("data_entry:general_journal"))

        elif "duplicate_split" in request.POST:
            sp_id = request.POST.get("sp_id")
            for sp in splits:
                if sp["sp_id"] == sp_id:
                    dup_sp = sp.copy()
                    dup_sp["sp_id"] = str(uuid.uuid4())
                    splits.append(dup_sp)
                    request.session.modified = True
                    message.success(
                        request,
                        f"Split duplicated successfully: {sp['ac_name']} ({sp['ac_code']}) | {sp['t_sp']}: {sp['am']}",
                    )
                    return redirect(reverse("data_entry:general_journal"))

            message.error(
                request, "Split with id: {sp_id} not found, duplication failed"
            )
            return redirect(reverse("data_entry:general_journal"))

        elif "edit_split" in request.POST:
            sp_id = request.POST.get("sp_id")
            for sp in splits:
                if sp["sp_id"] == sp_id:
                    data = {
                        "ac": str(sp["ac"]),
                        "t_sp": sp["t_sp"],
                        "am": sp["am"],
                    }

                    split_form = SplitForm(initial=data, prefix="split")
                    # dynamically add the session_sp_id field as a hidden input
                    split_form.fields["session_sp_id"] = forms.CharField(
                        widget=forms.HiddenInput(), initial=sp_id
                    )
                    message.info(request, "Editing Split")
                    break
            else:
                message.error(
                    request, "Split with id: {sp_id} not found, editing failed"
                )
                return redirect(reverse("data_entry:general_journal"))

        elif "update_split" in request.POST:
            session_sp_id = request.POST.get("split-session_sp_id")
            split_form = SplitForm(request.POST, prefix="split")
            if split_form.is_valid():
                for sp in splits:
                    if sp["sp_id"] == session_sp_id:
                        ac = split_form.cleaned_data["ac"]
                        ac_pk = ac.pk
                        ac_code = ac.code
                        ac_name = ac.name

                        t_sp = split_form.cleaned_data["t_sp"]
                        am = str(split_form.cleaned_data["am"])

                        sp.update(
                            {
                                "ac": ac_pk,
                                "ac_code": ac_code,
                                "ac_name": ac_name,
                                "t_sp": t_sp,
                                "am": am,
                            }
                        )
                        request.session.modified = True

                        message.success(
                            request,
                            f"Split successfully updated: {ac_name} ({ac_code}) | {t_sp}: {am}",
                        )
                        return redirect(reverse("data_entry:general_journal"))

                # if the loop completes without finding a matching sp_id
                message.error(
                    request,
                    "Split with id: {session_sp_id} not found, updating failed",
                )
                return redirect(reverse("data_entry:general_journal"))
            else:
                # if the form is not valid, re-render the form with the errors and the session_sp_id field
                split_form.fields["session_sp_id"] = forms.CharField(
                    widget=forms.HiddenInput(), initial=session_sp_id
                )

    session_bals = session_balances(splits)

    context = {
        "split_form": split_form,
        "transaction_form": transaction_form,
        "splits": splits,
        "session_bals": session_bals,
    }

    return render(request, template, context)


def cancel_transaction(request):
    if "splits" not in request.session:
        raise TypeError("None is not a session split")
    request.session["splits"] = []

    return redirect(reverse("data_entry:general_journal"))


def transaction_list(request):
    template = "data_entry/transaction_list.html"

    loaded_transactions = (
        Transaction.objects.prefetch_related("split_set")
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
