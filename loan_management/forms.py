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

    def clean(self):
        cleaned_data = super().clean()
        payment_type = cleaned_data.get("payment_type")
        amount = cleaned_data.get("amount")

        if payment_type == "custom":
            if not amount:
                raise forms.ValidationError("Custom amount is required")
            if amount <= 0:
                raise forms.ValidationError("Custom amount must be greater than zero")

        return cleaned_data


class LoanDisbursementForm(forms.Form):
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

    def clean(self):
        cleaned_data = super().clean()
        amount = cleaned_data.get("amount")

        if not amount:
            raise forms.ValidationError("Amount is required")
        if amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero")

        return cleaned_data
