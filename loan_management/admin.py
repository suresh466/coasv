from django.contrib import admin

from loan_management.models import Loan, LoanPayment

admin.site.register(Loan)
admin.site.register(LoanPayment)
