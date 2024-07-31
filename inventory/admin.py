from django.contrib import admin

from inventory.models import InventoryItem, Sale

admin.site.register(InventoryItem)
admin.site.register(Sale)
