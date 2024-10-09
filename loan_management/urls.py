from django.urls import path

from loan_management import views

app_name = "loan"

urlpatterns = [
    path("", views.loans, name="loans"),
    path("<int:id>/", views.loan, name="loan"),
    path("<int:id>/disburse", views.disburse_loan, name="disburse_loan"),
]
