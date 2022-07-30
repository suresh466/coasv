from django.urls import path

from ledgers import views

app_name = 'ledgers'
urlpatterns = [
    path('general_ledger/', views.general_ledger, name='general_ledger'),
]
