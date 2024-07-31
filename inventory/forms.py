from django.forms import ModelForm

from inventory.models import Sale


class SaleForm(ModelForm):
    class Meta:
        model = Sale
        fields = ("item", "quantity")
