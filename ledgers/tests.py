from django.test import TestCase
from django.urls import reverse

from coasc.models import ImpersonalAccount, Split, Transaction


class GeneralLedgerViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.single_ac1 = ImpersonalAccount.objects.create(
                name='single_ac1', code='1', type_ac='AS')
        cls.single_ac2 = ImpersonalAccount.objects.create(
                name='single_ac2', code='2', type_ac='LI')
        tx = Transaction.objects.create(description='demo desc')
        Split.objects.create(
                account=cls.single_ac1, type_split='dr',
                amount=100, transaction=tx)
        Split.objects.create(
                account=cls.single_ac2, type_split='cr',
                amount=100, transaction=tx)

    def test_uses_general_ledger_template(self):
        response = self.client.get(reverse('ledgers:general_ledger'))
        self.assertTemplateUsed(response, 'ledgers/general_ledger.html')

    def test_passes_accounts_to_template_as_expected(self):
        response = self.client.get(reverse('ledgers:general_ledger'))
        self.assertIn('accounts_data', response.context)
        accounts_data = response.context['accounts_data']
        self.assertEqual(accounts_data[0]['account_code'], '1')
        self.assertEqual(accounts_data[1]['account_code'], '2')
