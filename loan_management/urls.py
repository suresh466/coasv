from django.urls import path

from loan_management import views

app_name = "loan"

urlpatterns = [
    path("", views.loans, name="loans"),
]
