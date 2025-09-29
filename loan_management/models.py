from decimal import Decimal

from coasc.models import Ac, Member, Split, Transaction
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


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

    # default rounding method is round_half_even
    TWOPLACES = Decimal("0.01")  # round to two decimal places
    WHOLE = Decimal("1")  # round to nearest whole number

    id = models.AutoField(primary_key=True)
    current_term = models.IntegerField(default=1)
    member = models.ForeignKey(Member, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    disbursed_amount = models.DecimalField(
        max_digits=15, decimal_places=2, default=0.00
    )
    outstanding_principal = models.DecimalField(
        max_digits=15, decimal_places=2, default=0.00
    )
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    started_at = models.DateTimeField(default=timezone.now)
    # make status only editable by staff who can approve loans
    status = models.CharField(
        max_length=20, choices=LOAN_STATUS_CHOICES, default=PENDING
    )
    purpose = models.TextField()
    #  what to do for multiple disbursements, save the latest date or save all dates
    disbursed_at = models.DateTimeField(null=True, blank=True)
    minimum_payment = models.DecimalField(
        max_digits=15, decimal_places=2, default=100.00
    )

    def __str__(self):
        return f"Loan #{self.id} - {self.member.name} - {self.amount}"

    def clean(self):
        if self.amount < 0:
            raise ValidationError("Principal amount must be positive")

    def disburse(self, amount):
        # todo: only accept decimal with two decimal places
        """
        not decided on if want to store each disbursement seperately yet
        """
        if self.status not in (self.APPROVED, self.ACTIVE):
            print("cannot disburse loan, loan not approved")
            return
        total_disburse = self.disbursed_amount + amount
        if total_disburse > self.amount:
            print("cannot disburse more than loan amount")
            return

        self.disbursed_at = timezone.now()
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

    def process_payment(self, interest_amount=0, principal_amount=0):
        # TODO: only accept decimal with two decimal places
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
            raise ValidationError("Loan needs to be active to make a payment")
        if interest_amount is None or principal_amount is None:
            raise ValidationError("Amount is None")
        if interest_amount == 0 and principal_amount == 0:
            raise ValidationError("Amount is 0")

        interest_debit = Ac.objects.get(code="80")
        interest_credit = Ac.objects.get(code="160.2")
        principal_debit = Ac.objects.get(code="80")
        principal_credit = Ac.objects.get(code="110")

        self.process_interest(interest_amount, interest_debit, interest_credit)
        self.process_principal(principal_amount, principal_debit, principal_credit)

        self.save()

        if self.outstanding_principal == Decimal("0.00"):
            self.status = self.FULLYPAID
            self.save()

    def process_interest(self, amount, debit_account, credit_account):
        # todo: only accept decimal with two places
        if amount < Decimal("0.00"):
            print("amount must be a positive number")
            return

        tx = Transaction.objects.create(
            desc=f"Interest-payment for Loan #{self.id} of amount {amount}"
        )
        Split.objects.create(tx=tx, ac=debit_account, t_sp="dr", am=amount)
        Split.objects.create(tx=tx, ac=credit_account, t_sp="cr", am=amount)

        InterestPayment.objects.create(
            term=self.current_term,
            loan=self,
            amount=amount,
            payment_date=timezone.now(),
            transaction=tx,
            debit_account=debit_account,
            credit_account=credit_account,
        )

    def process_principal(self, amount, debit_account, credit_account):
        # todo: only accept decimal with two places
        if amount < Decimal("0.00"):
            print("amount needs to be a positive number greater than 0")
            return

        if amount > self.outstanding_principal:
            extra_amount = amount - self.outstanding_principal
            print(
                f"paying more than owed; outstanding_principal: {self.outstanding_principal}, paying: {amount} which is: {extra_amount} more than required principal"
            )
            return

        tx = Transaction.objects.create(
            desc=f"Principal-payment for Loan #{self.id} of amount {amount}"
        )
        Split.objects.create(tx=tx, ac=debit_account, t_sp="dr", am=amount)
        Split.objects.create(tx=tx, ac=credit_account, t_sp="cr", am=amount)

        PrincipalPayment.objects.create(
            term=self.current_term,
            loan=self,
            amount=amount,
            payment_date=timezone.now(),
            transaction=tx,
            debit_account=debit_account,
            credit_account=credit_account,
        )

        self.outstanding_principal -= amount
        self.save()


class InterestPayment(models.Model):
    id = models.AutoField(primary_key=True)
    term = models.IntegerField()
    loan = models.ForeignKey(Loan, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    payment_date = models.DateTimeField(default=timezone.now)
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
    id = models.AutoField(primary_key=True)
    term = models.IntegerField()
    loan = models.ForeignKey(Loan, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    payment_date = models.DateTimeField(default=timezone.now)
    transaction = models.OneToOneField(Transaction, on_delete=models.PROTECT)
    debit_account = models.ForeignKey(
        Ac, related_name="principal_payment_debits", on_delete=models.PROTECT
    )
    credit_account = models.ForeignKey(
        Ac, related_name="principal_payment_credits", on_delete=models.PROTECT
    )

    def __str__(self):
        return f"Payment of {self.amount} for Loan #{self.loan.id}"
