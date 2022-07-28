from django.test import TestCase
from django.urls import reverse

from coasc.models import ImpersonalAccount, Split


class GeneranJournalViewTest(TestCase):
    def test_uses_general_journal_template(self):
        response = self.client.get(reverse('data_entry:general_journal'))

        self.assertTemplateUsed(response, 'data_entry/general_journal.html')

    def test_can_save_a_POST_request(self):
        single_ac1 = ImpersonalAccount.objects.create(
                name='single_ac1', type_ac='AS', code='1')
        data = {'account': single_ac1.pk, 'type_split': 'dr', 'amount': '100'}
        url = reverse('data_entry:general_journal')
        self.client.post(url, data=data)

        saved_splits = Split.objects.all()

        self.assertEqual(saved_splits.count(), 1)
        self.assertEqual(saved_splits[0].account, single_ac1)
        self.assertEqual(saved_splits[0].type_split, 'dr')
        self.assertEqual(saved_splits[0].amount, 100)

    def test_redirects_after_POST(self):
        single_ac1 = ImpersonalAccount.objects.create(
                name='single_ac1', type_ac='AS', code='1')
        data = {'account': single_ac1.pk, 'type_split': 'dr', 'amount': '100'}
        url = reverse('data_entry:general_journal')
        response = self.client.post(url, data=data)

        self.assertRedirects(response, url)
