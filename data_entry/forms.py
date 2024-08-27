from coasc.models import Ac, Split, Transaction
from django.forms import ModelForm


class SplitForm(ModelForm):
    class Meta:
        model = Split
        fields = ("ac", "t_sp", "am")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Get all accounts that are not parent accounts
        queryset = Ac.objects.filter(ac__isnull=True)

        acs = Ac.objects.all()
        exclude_list = [ac.id for ac in acs if ac.is_parent]

        query_set = Ac.objects.exclude(id__in=exclude_list)
        self.fields["ac"].queryset = query_set


class TransactionForm(ModelForm):
    class Meta:
        model = Transaction
        fields = ("tx_date", "desc")
