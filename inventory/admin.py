from coasc.models import Ac
from django.contrib import admin

from inventory.models import InventoryItem, Sale


class InventoryItemAdmin(admin.ModelAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ["debit_account", "credit_account"]:
            # Get all accounts and filter out parents
            all_accounts = Ac.objects.all()
            non_parent_ids = [ac.id for ac in all_accounts if not ac.is_parent]
            kwargs["queryset"] = Ac.objects.filter(id__in=non_parent_ids)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class SaleAdmin(admin.ModelAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ["debit_account", "credit_account"]:
            # Get all accounts and filter out parents
            all_accounts = Ac.objects.all()
            non_parent_ids = [ac.id for ac in all_accounts if not ac.is_parent]
            kwargs["queryset"] = Ac.objects.filter(id__in=non_parent_ids)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(InventoryItem, InventoryItemAdmin)
admin.site.register(Sale, SaleAdmin)
