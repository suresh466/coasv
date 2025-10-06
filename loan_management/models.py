import calendar
from datetime import timedelta
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
    member = models.ForeignKey(Member, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
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
    disbursed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Loan #{self.id} - {self.member.name} - {self.amount}"

    def clean(self):
        if self.amount < 0:
            raise ValidationError("Principal amount must be positive")

    def disburse(self):
        # todo: only accept decimal with two decimal places
        """
        not decided on if want to store each disbursement seperately yet
        """
        if self.status != Loan.APPROVED:
            raise ValueError("Loan not approved or already disbursed")

        self.disbursed_at = timezone.now()
        self.status = self.ACTIVE
        self.outstanding_principal = self.amount
        self.save()

        debit_account = Ac.objects.get(code="110")
        credit_account = Ac.objects.get(code="80")

        tx = Transaction.objects.create(
            desc=f"Loan disbursed for Loan #{self.id} of amount {self.amount}"
        )
        Split.objects.create(tx=tx, ac=debit_account, am=self.amount, t_sp="dr")
        Split.objects.create(tx=tx, ac=credit_account, am=self.amount, t_sp="cr")

    def calculate_interest(self):
        billing_cycle = self.billingcycle_set.order_by("-date_created").first()  # type: ignore[attr-defined])
        prev_period_end = billing_cycle.period_end.date() if billing_cycle else None
        disbursed_date = self.disbursed_at.date()

        period_start = (
            prev_period_end + timedelta(days=1) if prev_period_end else disbursed_date
        )
        end_of_month = calendar.monthrange(period_start.year, period_start.month)[1]
        period_end = period_start.replace(day=end_of_month)
        days = end_of_month - period_start.day + 1
        leap_year = calendar.isleap(period_start.year)

        if leap_year:
            amount = (
                self.outstanding_principal * (self.interest_rate / 100) * days / 366
            )
        else:
            amount = (
                self.outstanding_principal * (self.interest_rate / 100) * days / 365
            )
        return amount, period_start, period_end, days, leap_year

    def process_interest(self, amount, period_start, period_end):
        debit = Ac.objects.get(code="80")
        credit = Ac.objects.get(code="160.2")

        tx = Transaction.objects.create(
            desc=f"Interest-payment for Loan #{self.id} of amount {amount}"
        )
        Split.objects.create(tx=tx, ac=debit, t_sp="dr", am=amount)
        Split.objects.create(tx=tx, ac=credit, t_sp="cr", am=amount)

        billing_cycle = BillingCycle.objects.create(
            loan=self,
            amount=amount,
            period_start=period_start,
            period_end=period_end,
        )

        InterestPayment.objects.create(
            loan=self,
            amount=amount,
            payment_date=timezone.now(),
            transaction=tx,
            billing_cycle=billing_cycle,
            debit_account=debit,
            credit_account=credit,
        )

    def process_principal(self, amount):
        debit = Ac.objects.get(code="80")
        credit = Ac.objects.get(code="110")

        if amount > self.outstanding_principal:
            extra_amount = amount - self.outstanding_principal
            print(
                f"paying more than owed; outstanding_principal: {self.outstanding_principal}, paying: {amount} which is: {extra_amount} more than required principal"
            )
            return

        tx = Transaction.objects.create(
            desc=f"Principal-payment for Loan #{self.id} of amount {amount}"
        )
        Split.objects.create(tx=tx, ac=debit, t_sp="dr", am=amount)
        Split.objects.create(tx=tx, ac=credit, t_sp="cr", am=amount)

        PrincipalPayment.objects.create(
            loan=self,
            amount=amount,
            payment_date=timezone.now(),
            transaction=tx,
            debit_account=debit,
            credit_account=credit,
        )

        self.outstanding_principal -= amount
        if self.outstanding_principal == Decimal("0.00"):
            self.status = self.FULLYPAID
        self.save()


class BillingCycle(models.Model):
    PAID = "paid"
    OVERDUE = "overdue"
    STATUS_CHOICES = [
        (PAID, "Paid"),
        (OVERDUE, "Overdue"),
    ]

    date_created = models.DateTimeField(default=timezone.now)
    id = models.AutoField(primary_key=True)
    loan = models.ForeignKey(Loan, on_delete=models.PROTECT)
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PAID)
    amount = models.DecimalField(max_digits=15, decimal_places=2)


class InterestPayment(models.Model):
    id = models.AutoField(primary_key=True)
    loan = models.ForeignKey(Loan, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    payment_date = models.DateTimeField(default=timezone.now)
    transaction = models.OneToOneField(Transaction, on_delete=models.PROTECT)
    billing_cycle = models.ForeignKey(BillingCycle, on_delete=models.PROTECT)
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
