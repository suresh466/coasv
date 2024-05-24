from django.urls import path

from ledgers import views

app_name = "ledgers"
urlpatterns = [
    path("general_ledger/", views.general_ledger, name="general_ledger"),
    path("ledger/<code>/", views.ledger, name="ledger"),
    path("purchase_ledger/", views.purchase_ledger, name="purchase_ledger"),
    path("sales_ledger/", views.sales_ledger, name="sales_ledger"),
    path("assets_ledger/", views.assets_ledger, name="assets_ledger"),
    path("liabilities/", views.liabilities_ledger, name="liabilities_ledger"),
]
