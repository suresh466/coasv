from django import forms

from loan_management.models import PrincipalPayment


class LoanPaymentForm(forms.Form):
    interest_amount = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(
            attrs={
                "class": "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm",
                "placeholder": "Interest Amount",
            }
        ),
    )
    principal_amount = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(
            attrs={
                "class": "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm",
                "placeholder": "Principal Amount",
            }
        ),
    )

    def clean(self):
        cleaned_data = super().clean()
        interest = cleaned_data.get("interest_amount") or 0
        principal = cleaned_data.get("principal_amount") or 0
        cleaned_data["interest_amount"] = interest
        cleaned_data["principal_amount"] = principal
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
