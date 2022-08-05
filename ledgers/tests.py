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

    def test_passes_tables_to_template_as_expected(self):
        response = self.client.get(reverse('ledgers:general_ledger'))
        self.assertIn('tables', response.context)
        tables = response.context['tables']
        self.assertEqual(tables[0]['code'], '1')
        self.assertEqual(tables[1]['code'], '2')


class LedgerViewTest(TestCase):
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

    def test_uses_ledger_template(self):
        response = self.client.get(reverse('ledgers:ledger', args=[1]))
        self.assertTemplateUsed(response, 'ledgers/ledger.html')

    def test_redirects_if_code_is_None(self):
        response = self.client.get(reverse('ledgers:ledger', args=[None]))
        self.assertRedirects(response, reverse('ledgers:general_ledger'))

    def test_redirects_if_account_does_not_exist(self):
        response = self.client.get(reverse('ledgers:ledger', args=[3]))
        self.assertRedirects(response, reverse('ledgers:general_ledger'))

    def test_passes_table_to_template_as_expected(self):
        response = self.client.get(reverse('ledgers:ledger', args=[1]))
        self.assertIn('table', response.context)
        table = response.context['table']
        self.assertEqual(table['code'], '1')
