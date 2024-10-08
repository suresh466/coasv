from decimal import Decimal

from django import forms


class LoanPaymentForm(forms.Form):
    PAYMENT_CHOICES = [
        ("regular", "Regular Payment"),
        ("custom", "Custom Amount"),
        ("payoff", "Payoff Loan"),
    ]

    payment_type = forms.ChoiceField(
        choices=PAYMENT_CHOICES,
        widget=forms.RadioSelect(attrs={"class": "form-radio"}),
        initial="regular",
    )

    amount = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(
            attrs={
                "class": "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm",
                "placeholder": "Enter amount",
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        self.loan = kwargs.pop("loan", None)
        self.next_payment_amount = kwargs.pop("next_payment_amount", Decimal("0.00"))
        self.payoff_amount = kwargs.pop("payoff_amount", Decimal("0.00"))
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        payment_type = cleaned_data.get("payment_type")
        amount = cleaned_data.get("amount")

        if payment_type == "regular":
            cleaned_data["amount"] = self.next_payment_amount
        elif payment_type == "payoff":
            cleaned_data["amount"] = self.payoff_amount
        elif payment_type == "custom":
            if not amount:
                raise forms.ValidationError("Custom amount is required")
            if amount < self.loan.minimum_payment:
                raise forms.ValidationError(
                    f"Amount must be at least {self.loan.minimum_payment}"
                )

        return cleaned_data
