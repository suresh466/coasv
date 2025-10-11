from django.urls import path

from loan_management import views

app_name = "loan"

urlpatterns = [
    path("", views.loans, name="loans"),
    path("<int:id>/", views.loan, name="loan"),
    path("<int:id>/payment", views.payment, name="payment"),
    path("<int:id>/disburse", views.disburse, name="disburse"),
    path("<int:id>/pay-interest", views.pay_interest, name="pay_interest"),
    path(
        "<int:id>/calculate-interest",
        views.calculate_interest,
        name="calculate_interest",
    ),
]
