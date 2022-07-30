from django.forms import ModelForm

from coasc.models import Split, ImpersonalAccount


class SplitForm(ModelForm):
    class Meta:
        model = Split
        fields = ('account', 'type_split', 'amount')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        exclude_list = []
        for account in ImpersonalAccount.objects.all():
            if account.who_am_i()['parent']:
                exclude_list.append(account.id)

        query_set = ImpersonalAccount.objects.exclude(
                id__in=exclude_list)
        self.fields['account'].queryset = query_set
