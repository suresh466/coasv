from django.contrib import admin

from loan_management.models import BillingCycle, InterestPayment, Loan, PrincipalPayment

admin.site.register(Loan)
admin.site.register(InterestPayment)
admin.site.register(PrincipalPayment)
admin.site.register(BillingCycle)
