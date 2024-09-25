from django.contrib import admin

from loan_management.models import InterestPayment, Loan, PrincipalPayment

admin.site.register(Loan)
admin.site.register(InterestPayment)
admin.site.register(PrincipalPayment)
