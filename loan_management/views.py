from django.shortcuts import render

from loan_management.models import Loan

# Create your views here.


def loans(request):
    loans = Loan.objects.all()
    template = "loan_management/loans.html"
    context = {"loans": loans}
    return render(request, template, context)
