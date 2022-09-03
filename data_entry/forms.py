from django.forms import ModelForm

from coasc.models import Split, Ac


class SplitForm(ModelForm):
    class Meta:
        model = Split
        fields = ('ac', 't_sp', 'am')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        acs = Ac.objects.all()
        exclude_list = [ac.id for ac in acs if ac.who_am_i()['parent']]

        query_set = Ac.objects.exclude(id__in=exclude_list)
        self.fields['ac'].queryset = query_set
