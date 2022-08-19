from django.urls import path

from fstatements import views

app_name = 'fs'
urlpatterns = [
    path('smoke/', views.smoke, name='smoke'),
]
