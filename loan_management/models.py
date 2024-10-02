from datetime import date, datetime
from decimal import ROUND_CEILING, Decimal
from math import ceil

from coasc.models import Ac, Member, Split, Transaction
from django.core.exceptions import ValidationError
from django.db import models


class Loan(models.Model):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"
    FULLYPAID = "FULLYPAID"
    CANCELLED = "CANCELLED"
    DEFAULTED = "DEFAULTED"

    LOAN_STATUS_CHOICES = [
        (PENDING, "Pending"),
        (APPROVED, "Approved"),
        (ACTIVE, "Active"),
        (FULLYPAID, "Fully Paid"),
        (DEFAULTED, "Defaulted"),
    ]

    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"

    LOAN_PAYMENT_FREQUENCY = [(MONTHLY, "Monthly"), (YEARLY, "Yearly")]

    # default rounding method is round_half_even
    TWOPLACES = Decimal("0.01")  # round to two decimal places
    WHOLE = Decimal("1")  # round to nearest whole number

    member = models.ForeignKey(Member, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    disbursed_amount = models.DecimalField(
        max_digits=15, decimal_places=2, default=0.00
    )
    outstanding_principal = models.DecimalField(
        max_digits=15, decimal_places=2, default=0.00
    )
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    term = models.IntegerField(help_text="Loan term in months")
    started_at = models.DateTimeField(null=True, blank=True)
    end_at = models.DateTimeField(null=True, blank=True)
    # make status only editable by staff who can approve loans
    status = models.CharField(
        max_length=20, choices=LOAN_STATUS_CHOICES, default=PENDING
    )
    payment_frequency = models.CharField(
        max_length=7, choices=LOAN_PAYMENT_FREQUENCY, default=MONTHLY
    )
    purpose = models.TextField()
    # what to do for multiple disbursements, save the latest date or save all dates
    disbursed_at = models.DateTimeField(null=True, blank=True)
    minimum_payment = models.DecimalField(
        max_digits=15, decimal_places=2, default=100.00
    )

    def __str__(self):
        return f"Loan #{self.id} - {self.member.name} - {self.amount}"

    def clean(self):
        if self.amount <= 0:
            raise ValidationError("Principal amount must be positive")

    def is_final_payment(self):
        # todo: only accept decimal with two decimal places
        remaining_term = self.term - (
            (date.today() - self.disbursed_at.date()).days // 30
        )

        # todo: look into final payment in case amount > minimum_payment
        # and not the last month of the term period (amount == annual_interest + outstanding_principal)
        # if self.outstanding_principal == calculated_principal then final payment !!

        return remaining_term == 1 or self.outstanding_principal <= self.minimum_payment

    def disburse(self, amount):
        # todo: only accept decimal with two decimal places
        """
        not decided on if want to store each disbursement seperately yet
        """
        if self.status not in (self.APPROVED, self.ACTIVE):
            print("cannot disburse loan, loan not approved")
            return
        total_disburse = (self.disbursed_amount + amount).quantize(self.TWOPLACES)
        if total_disburse > self.amount:
            print("cannot disburse more than loan amount")
            return

        self.disbursed_at = datetime.now()
        self.status = self.ACTIVE
        self.outstanding_principal += amount
        self.disbursed_amount += amount
        self.save()

        debit_account = Ac.objects.get(code="110")
        credit_account = Ac.objects.get(code="80")

        tx = Transaction.objects.create(
            desc=f"Loan disbursed for Loan #{self.id} of amount {amount}"
        )
        Split.objects.create(tx=tx, ac=debit_account, am=amount, t_sp="dr")
        Split.objects.create(tx=tx, ac=credit_account, am=amount, t_sp="cr")

    def calculate_next_payment_amount(self, payoff=False):
        if self.status != self.ACTIVE:
            print("cannot calculate payoff amount, loan is not active")
            return

        if self.is_final_payment():
            payoff = True

        # Don't round the amounts to the nearest whole number
        if payoff:
            interest = (
                self.interest_rate / Decimal("100.00") * self.outstanding_principal
            ).quantize(self.TWOPLACES)
            principal = self.outstanding_principal
            total = (self.outstanding_principal + interest).quantize(self.TWOPLACES)

            return interest, principal, total
        else:
            annual_interest = (
                self.interest_rate / Decimal("100.00") * self.outstanding_principal
            )

            remaining_term = self.term - (
                (date.today() - self.disbursed_at.date()).days // 30
            )
            if self.payment_frequency == self.MONTHLY:
                installments = remaining_term
            else:
                installments = ceil(remaining_term / 12)

            # make it decimal because in following calculations both operands being decimal is better
            installments = Decimal(installments)

            interest = (annual_interest / installments).quantize(self.TWOPLACES)
            principal = (self.outstanding_principal / installments).quantize(
                self.TWOPLACES
            )
            total = (interest + principal).quantize(self.TWOPLACES)

            # Not rounding the final payment to make up for rounded amount in previous payments
            # and rounding the rest of the payments for convinience
            if principal != self.outstanding_principal:
                rounded_total = (interest + principal).quantize(
                    self.WHOLE, rounding=ROUND_CEILING
                )
                rounding_amount = (rounded_total - total).quantize(self.TWOPLACES)
                rounded_principal = principal + rounding_amount

                # for edge cases like:
                # minimum payment = 100
                # outstanding_principal = 100.50
                # calculated_principal = 101 (due to adding the additional rounding_amount)
                # since outstanding_principal > minimum_payment it is not caught by is_final_payment
                # so, principal + rounding_amount > owed principal. This could happen towards the end of the loan payment
                # it is basically an edge last payment case
                if rounded_principal > self.outstanding_principal:
                    principal = self.outstanding_principal
                    total = (interest + principal).quantize(self.TWOPLACES)
                else:
                    principal = rounded_principal
                    total = rounded_total

        return interest, principal, total

    def generate_repayment_schedule(self):
        """
        redo this method to generate expected payment amounts after each payment
        for the whole payment term. Interest decreases with each payment.
        like reducing balance method but with decreasing emi amount after each payment.
        OR
        make it able to do above explained along with redicing-balance with fixed emi.
        """
        if self.status != self.ACTIVE:
            print("cannot generate repayment schedule loan is not active")
            return

        annual_interest = (
            self.interest_rate / Decimal("100.00") * self.outstanding_principal
        )
        total_amount = self.outstanding_principal + annual_interest
        remaining_term = self.term - (
            (date.today() - self.disbursed_at.date()).days // 30
        )

        if self.payment_frequency == self.MONTHLY:
            installments = remaining_term
        else:
            installments = remaining_term / 12

        installment_amount = total_amount / installments

        return installment_amount

    def process_payment(self, amount, payoff=False):
        # todo: only accept decimal with two decimal places
        """
        pay interest and principal

        Attributes:
            amount: Total amount paid by the borrower
            interest_debit (test_default=80): account to be debited for interest payment
            interest_credit (test_default=160.2): account to be credited for interest payment
            principal_debit (test_default=80): account to be debited for principal payment
            principal_credit (test_default=110): account to be credited for principal payment
        """
        if self.status != self.ACTIVE:
            print("loan needs to be active to make a payment")
            return

        interest_debit = Ac.objects.get(code="80")
        interest_credit = Ac.objects.get(code="160.2")
        principal_debit = Ac.objects.get(code="80")
        principal_credit = Ac.objects.get(code="110")

        annual_interest = (
            self.interest_rate / Decimal("100.00") * self.outstanding_principal
        )

        remaining_term = self.term - (
            (date.today() - self.disbursed_at.date()).days // 30
        )

        if self.payment_frequency == self.MONTHLY:
            installments = remaining_term
        else:
            installments = remaining_term / 12

        interest_amount = (
            annual_interest if payoff else (annual_interest / installments)
        ).quantize(self.TWOPLACES)

        principal_amount = (amount - interest_amount).quantize(self.TWOPLACES)

        if amount <= interest_amount:
            interest_amount = amount
            self.process_interest(interest_amount, interest_debit, interest_credit)
            return

        # create method for interest calculation for the next payment maybe
        self.process_interest(interest_amount, interest_debit, interest_credit)
        self.process_principal(principal_amount, principal_debit, principal_credit)

        if self.outstanding_principal == Decimal("0.00"):
            self.status = self.FULLYPAID
            self.end_date = datetime.now()
            self.save()

    def process_interest(self, amount, debit_account, credit_account):
        # todo: only accept decimal with two places
        if amount <= Decimal("0.00"):
            print("amount must be a positive number")
            return

        tx = Transaction.objects.create(
            desc=f"Loan Payment (interest) for Loan #{self.id} of amount {amount}"
        )
        Split.objects.create(tx=tx, ac=debit_account, t_sp="dr", am=amount)
        Split.objects.create(tx=tx, ac=credit_account, t_sp="cr", am=amount)

        InterestPayment.objects.create(
            loan=self,
            amount=amount,
            payment_date=datetime.now(),
            transaction=tx,
            debit_account=debit_account,
            credit_account=credit_account,
        )

    def process_principal(self, amount, debit_account, credit_account):
        # todo: only accept decimal with two places
        if amount <= Decimal("0.00"):
            print("amount needs to be a positive number greater than 0")
            return

        if amount > self.outstanding_principal:
            extra_amount = amount - self.outstanding_principal
            print(
                f"cant pay more than owed, you owe {self.outstanding_principal} but you are paying {amount} which is {extra_amount} more than required"
            )
            return

        tx = Transaction.objects.create(
            desc=f"Loan Payment (principal) for Loan #{self.id} of amount {amount}"
        )
        Split.objects.create(tx=tx, ac=debit_account, t_sp="dr", am=amount)
        Split.objects.create(tx=tx, ac=credit_account, t_sp="cr", am=amount)

        PrincipalPayment.objects.create(
            loan=self,
            amount=amount,
            payment_date=datetime.now(),
            transaction=tx,
            debit_account=debit_account,
            credit_account=credit_account,
        )

        self.outstanding_principal -= amount
        self.save()


# maybe consolidate interest payment and principal payment models (if it helps with late payments later)
class InterestPayment(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    payment_date = models.DateTimeField()
    transaction = models.OneToOneField(Transaction, on_delete=models.PROTECT)
    debit_account = models.ForeignKey(
        Ac, related_name="interest_payment_debits", on_delete=models.PROTECT
    )
    credit_account = models.ForeignKey(
        Ac, related_name="interest_payment_credits", on_delete=models.PROTECT
    )

    def __str__(self):
        return f"{self.loan.id} - {self.amount}"


class PrincipalPayment(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    payment_date = models.DateTimeField()
    transaction = models.OneToOneField(Transaction, on_delete=models.PROTECT)
    debit_account = models.ForeignKey(
        Ac, related_name="principal_payment_debits", on_delete=models.PROTECT
    )
    credit_account = models.ForeignKey(
        Ac, related_name="principal_payment_credits", on_delete=models.PROTECT
    )

    def __str__(self):
        return f"Payment of {self.amount} for Loan #{self.loan.id}"
