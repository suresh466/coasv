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


class SaveTransactionViewTest(TestCase):
    @classmethod
    def setUpTestData(self):
        self.single_ac1 = ImpersonalAccount.objects.create(
                name='single_ac1', type_ac='AS', code='1')
        self.single_ac2 = ImpersonalAccount.objects.create(
                name='single_ac2', type_ac='AS', code='2')

    def test_raises_exception_if_splits_is_None(self):
        url = reverse('data_entry:save_transaction')
        data = {'description': 'demo desc'}

        with self.assertRaisesMessage(
                TypeError, 'None is not a session split'):
            self.client.post(url, data=data)

    def test_can_save_POST_request(self):
        session = self.client.session
        session['splits'] = [
                {'account': self.single_ac1.pk, 'type_split': 'dr',
                    'amount': '100'},
                {'account': self.single_ac2.pk, 'type_split': 'cr',
                    'amount': '100'}
        ]
        session.save()

        url = reverse('data_entry:save_transaction')
        data = {'description': 'demo desc'}
        self.client.post(url, data=data)

        single_ac1_balances = self.single_ac1.current_balance()
        single_ac2_balances = self.single_ac2.current_balance()

        self.assertEqual(single_ac1_balances['dr_sum'], 100)
        self.assertEqual(single_ac1_balances['cr_sum'], 0)
        self.assertEqual(single_ac2_balances['dr_sum'], 0)
        self.assertEqual(single_ac2_balances['cr_sum'], 100)
