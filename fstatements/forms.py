from datetime import date

from django import forms


class DateFilterForm(forms.Form):
    # validatate that end date is greater than start date
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}),
        label="Start Date",
        help_text="Enter the start date in the format: YYYY-MM-DD",
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}),
        label="End Date",
        help_text="Enter the end date in the format: YYYY-MM-DD",
        initial=date.today(),
    )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date:
            if start_date > date.today():
                self.add_error(
                    "start_date", "Start date must be less than or equal to today"
                )
            if end_date < start_date:
                self.add_error("end_date", "End date must be greater than start date")
            if end_date > date.today():
                self.add_error(
                    "end_date", "End date must be less than or equal to today"
                )

        return cleaned_data
