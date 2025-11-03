import calendar
from datetime import date, timedelta
from decimal import Decimal
from itertools import chain
from operator import attrgetter

from coasc.models import Ac, Member, Split, Transaction
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Loan(TimeStampedModel):
    PENDING = "pending"
    APPROVED = "approved"
    ACTIVE = "active"
    FULLYPAID = "paid"
    DEFAULTED = "defaulted"

    LOAN_STATUS_CHOICES = [
        (PENDING, "Pending"),
        (APPROVED, "Approved"),
        (ACTIVE, "Active"),
        (FULLYPAID, "Paid"),
        (DEFAULTED, "Defaulted"),
    ]

    # default rounding method is round_half_even
    TWOPLACES = Decimal("0.01")  # round to two decimal places
    WHOLE = Decimal("1")  # round to nearest whole number

    started_at = models.DateTimeField(default=timezone.now)
    disbursed_at = models.DateTimeField(null=True, blank=True)
    member = models.ForeignKey(Member, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    outstanding_principal = models.DecimalField(
        max_digits=15, decimal_places=2, default=0.00
    )
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    # make status only editable by staff who can approve loans
    status = models.CharField(
        max_length=20, choices=LOAN_STATUS_CHOICES, default=PENDING
    )
    purpose = models.TextField()

    def __str__(self):
        return f"Loan #{self.id} - {self.member.name} - {self.amount}"

    def clean(self):
        if self.amount < 0:
            raise ValidationError("Principal amount must be positive")

    def approve(self):
        if self.status == self.PENDING:
            self.status = self.APPROVED
            self.save()
        else:
            raise ValueError("Loan Approval failed!")

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

    def calculate_fee(self):
        return Decimal(5.00)

    def calculate_interest(self, period_start=None, period_end=None, to_date=False):
        billing_cycle = self.billingcycle_set.order_by("-date_created").first()  # type: ignore[attr-defined])
        prev_period_end = billing_cycle.period_end.date() if billing_cycle else None
        disbursed_date = self.disbursed_at.date()

        if not period_start:
            period_start = (
                prev_period_end + timedelta(days=1)
                if prev_period_end
                else disbursed_date
            )
        if to_date:
            period_end = date.today()
        else:
            if not period_end:
                period_end = period_start.replace(
                    day=calendar.monthrange(period_start.year, period_start.month)[1]
                )
        days = (period_end - period_start).days + 1
        leap_year = calendar.isleap(period_start.year)

        if leap_year:
            total = self.outstanding_principal * (self.interest_rate / 100) * days / 366
        else:
            total = self.outstanding_principal * (self.interest_rate / 100) * days / 365

        return total, period_start, period_end, days, leap_year

    def calculate_days(self, amount):
        billing_cycle = self.billingcycle_set.order_by("-date_created").first()  # type: ignore[attr-defined])
        prev_period_end = billing_cycle.period_end.date() if billing_cycle else None
        disbursed_date = self.disbursed_at.date()

        period_start = (
            prev_period_end + timedelta(days=1) if prev_period_end else disbursed_date
        )
        period_end = period_start.replace(
            day=calendar.monthrange(period_start.year, period_start.month)[1]
        )

        days = (period_end - period_start).days + 1
        leap_year = calendar.isleap(period_start.year)
        year_days = 366 if leap_year else 365
        daily_interest = (
            self.outstanding_principal * (self.interest_rate / 100) * 1 / year_days
        )

        if daily_interest > amount:
            raise ValueError("Amount should at least cover one day of interest")

        full_month_interest = daily_interest * days
        if amount >= full_month_interest:
            amount_after_interest = amount - full_month_interest
            return amount_after_interest, period_end
        else:
            complete_days = int(amount / daily_interest)

            amount_after_interest = amount - (complete_days * daily_interest)
            period_end = period_start + timedelta(days=complete_days - 1)
            return amount_after_interest, period_end

    def overdue_cycles(self):
        return self.billingcycle_set.filter(status="overdue")

    @property
    def is_overdue(self):
        return self.overdue_cycles().exists()

    def generate_payment_history(self):
        interest_payments = self.interestpayment_set.select_related(
            "billing_cycle",
            "transaction",
        ).all()
        principal_payments = self.principalpayment_set.select_related(
            "transaction"
        ).all()

        # Combine and sort payments by date
        all_payments = sorted(
            chain(interest_payments, principal_payments), key=attrgetter("payment_at")
        )

        payment_history = []
        for payment in all_payments:
            if isinstance(payment, InterestPayment):
                payment_history.append(
                    {
                        "date": payment.payment_at.date(),
                        "type": "interest",
                        "amount": payment.amount,
                        "period_start": payment.billing_cycle.period_start.date(),
                        "period_end": payment.billing_cycle.period_end.date(),
                        "transaction": payment.transaction,
                    }
                )
            else:
                payment_history.append(
                    {
                        "date": payment.payment_at.date(),
                        "type": "principal",
                        "amount": payment.amount,
                        "transaction": payment.transaction,
                    }
                )

        return payment_history

    def process_fee(self, amount, billing_cycle):
        if amount <= 0:
            raise ValueError("Amount cannot be less than equal to 0")
        debit = Ac.objects.get(code="80")
        credit = Ac.objects.get(code="160.4")

        tx = Transaction.objects.create(
            desc=f"Interest-payment for Loan #{self.id} of amount {amount}"
        )
        Split.objects.create(tx=tx, ac=debit, t_sp="dr", am=amount)
        Split.objects.create(tx=tx, ac=credit, t_sp="cr", am=amount)

        FeePayment.objects.create(
            loan=self,
            amount=amount,
            payment_at=timezone.now(),
            transaction=tx,
            billing_cycle=billing_cycle,
            debit_account=debit,
            credit_account=credit,
        )

    def process_interest(self, amount, period_start, period_end):
        if amount <= 0:
            raise ValueError("Amount cannot be less than equal to 0")
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
            payment_at=timezone.now(),
            transaction=tx,
            billing_cycle=billing_cycle,
            debit_account=debit,
            credit_account=credit,
        )

    def process_principal(self, amount):
        if self.calculate_interest(to_date=True)[0] > 0:
            raise ValidationError("Interest due to date not paid")
        if amount > self.outstanding_principal:
            extra_amount = amount - self.outstanding_principal
            raise ValidationError(
                f"paying more than owed; outstanding_principal: {self.outstanding_principal}, paying: {amount} which is: {extra_amount} more than required principal"
            )

        debit = Ac.objects.get(code="80")
        credit = Ac.objects.get(code="110")

        tx = Transaction.objects.create(
            desc=f"Principal-payment for Loan #{self.id} of amount {amount}"
        )
        Split.objects.create(tx=tx, ac=debit, t_sp="dr", am=amount)
        Split.objects.create(tx=tx, ac=credit, t_sp="cr", am=amount)

        PrincipalPayment.objects.create(
            loan=self,
            amount=amount,
            payment_at=timezone.now(),
            transaction=tx,
            debit_account=debit,
            credit_account=credit,
        )

        self.outstanding_principal -= amount
        if self.outstanding_principal == Decimal("0.00"):
            self.status = self.FULLYPAID
        self.save()


class BillingCycle(TimeStampedModel):
    PAID = "paid"
    OVERDUE = "overdue"
    STATUS_CHOICES = [
        (PAID, "Paid"),
        (OVERDUE, "Overdue"),
    ]

    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    loan = models.ForeignKey(Loan, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PAID)
    amount = models.DecimalField(max_digits=15, decimal_places=2)


class FeePayment(TimeStampedModel):
    payment_at = models.DateTimeField(default=timezone.now)
    loan = models.ForeignKey(Loan, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    transaction = models.OneToOneField(Transaction, on_delete=models.PROTECT)
    billing_cycle = models.ForeignKey(BillingCycle, on_delete=models.PROTECT)
    debit_account = models.ForeignKey(
        Ac, related_name="fee_payment_debits", on_delete=models.PROTECT
    )
    credit_account = models.ForeignKey(
        Ac, related_name="fee_payment_credits", on_delete=models.PROTECT
    )

    def __str__(self):
        return f"{self.loan.id} - {self.amount}"


class InterestPayment(TimeStampedModel):
    payment_at = models.DateTimeField(default=timezone.now)
    loan = models.ForeignKey(Loan, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
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


class PrincipalPayment(TimeStampedModel):
    payment_at = models.DateTimeField(default=timezone.now)
    loan = models.ForeignKey(Loan, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    transaction = models.OneToOneField(Transaction, on_delete=models.PROTECT)
    debit_account = models.ForeignKey(
        Ac, related_name="principal_payment_debits", on_delete=models.PROTECT
    )
    credit_account = models.ForeignKey(
        Ac, related_name="principal_payment_credits", on_delete=models.PROTECT
    )

    def __str__(self):
        return f"Payment of {self.amount} for Loan #{self.loan.id}"
