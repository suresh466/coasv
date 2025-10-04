from django import forms

from loan_management.models import PrincipalPayment


class LoanPaymentForm(forms.Form):
    amount = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        required=True,
        widget=forms.NumberInput(
            attrs={
                "class": "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm",
                "placeholder": "Amount",
            }
        ),
    )

    credit_checkbox = forms.BooleanField(
        required=False,
        label="Loan Credit",
        widget=forms.CheckboxInput(
            attrs={
                "class": "h-4 w-4 text-indigo-600 border-gray-300 rounded",
            }
        ),
    )
