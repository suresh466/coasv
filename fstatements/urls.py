from django.urls import path

from fstatements import views

app_name = 'fs'
urlpatterns = [
    path('balance_sheet/', views.balance_sheet, name='balance_sheet'),
    path('trial_balance/', views.trial_balance, name='trial_balance'),
]
