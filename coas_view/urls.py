"""coas_view URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include

from data_entry import urls as data_entry_urls
from ledgers import urls as ledgers_urls
from fstatements import urls as fstatements_urls
from data_entry.views import general_journal
from inventory import urls as inventory

urlpatterns = [
    path("admin/", admin.site.urls),
    path("data_entry/", include(data_entry_urls)),
    path("ledgers/", include(ledgers_urls)),
    path("fs/", include(fstatements_urls)),
    path("inventory/", include(inventory)),
    path("", general_journal),
]
