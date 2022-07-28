from django.test import TestCase
from django.urls import reverse

from coasc.models import ImpersonalAccount


class GeneranJournalViewTest(TestCase):
    @classmethod
    def setUpTestData(self):
        self.single_ac1 = ImpersonalAccount.objects.create(
                name='single_ac1', type_ac='AS', code='1')

    def test_uses_general_journal_template(self):
        response = self.client.get(reverse('data_entry:general_journal'))

        self.assertTemplateUsed(response, 'data_entry/general_journal.html')

    def test_redirects_after_POST(self):
        data = {
                'account': self.single_ac1.pk,
                'type_split': 'dr', 'amount': '100'
        }
        url = reverse('data_entry:general_journal')
        response = self.client.post(url, data=data)

        self.assertRedirects(response, url)
