from django.urls import path

from data_entry import views

app_name = "data_entry"
urlpatterns = [
    path("general_journal/", views.general_journal, name="general_journal"),
    path("transaction_list/", views.transaction_list, name="transaction_list"),
    path("cancel_transaction/", views.cancel_transaction, name="cancel_transaction"),
]
