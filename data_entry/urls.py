from django.urls import path

from data_entry import views

app_name = 'data_entry'
urlpatterns = [
    path('general_journal/', views.general_journal, name='general_journal'),
    path('save_transaction/', views.save_transaction, name='save_transaction'),
]
