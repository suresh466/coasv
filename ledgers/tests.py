from django.test import TestCase
from django.urls import reverse

from coasc.models import ImpersonalAccount, Split, Transaction

from ledgers.views import generate_rows, generate_table


class GeneralLedgerViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.single_ac1 = ImpersonalAccount.objects.create(
                name='single_ac1', code='1', type_ac='AS')
        cls.single_ac2 = ImpersonalAccount.objects.create(
                name='single_ac2', code='2', type_ac='LI')
        cls.parent_ac1 = ImpersonalAccount.objects.create(
                name='parent_ac1', code='3', type_ac='EX')
        cls.child_ac1 = ImpersonalAccount.objects.create(
                name='child_ac1', code='3.1', parent_ac=cls.parent_ac1)
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
        tables = response.context['tables']

        self.assertIn('tables', response.context)
        self.assertEqual(len(tables), 3)
        self.assertEqual(tables[0]['code'], '1')
        self.assertEqual(tables[1]['code'], '2')
        self.assertEqual(tables[2]['code'], '3.1')


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
        table = response.context['table']

        self.assertIn('table', response.context)
        self.assertEqual(table['code'], '1')


class GenerateRowsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.single_ac1 = ImpersonalAccount.objects.create(
                name='single_ac1', code='1', type_ac='AS')
        tx = Transaction.objects.create(description='demo desc')

        Split.objects.create(
                account=cls.single_ac1, type_split='dr',
                amount=100, transaction=tx)
        Split.objects.create(
                account=cls.single_ac1, type_split='cr',
                amount=200, transaction=tx)

    def test_returns_emtpy_list_if_no_splits(self):
        splits = []
        rows = generate_rows(splits)
        self.assertFalse(rows)

    def test_returns_rows_as_expected(self):
        splits = self.single_ac1.split_set.all()
        rows = generate_rows(splits)

        row1 = {'debit': 100.00, 'credit': 0, 'difference': 100.00,
                'description': 'demo desc'}
        row2 = {'debit': 0, 'credit': 200.00, 'difference': -100.00,
                'description': 'demo desc'}
        expected_rows = [row1, row2]

        self.assertEqual(len(rows), 2)
        self.assertEqual(rows, expected_rows)


class GenerateTableTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.single_ac1 = ImpersonalAccount.objects.create(
                name='single_ac1', code='1', type_ac='AS')
        tx = Transaction.objects.create(description='demo desc')

        Split.objects.create(
                account=cls.single_ac1, type_split='dr',
                amount=100, transaction=tx)
        Split.objects.create(
                account=cls.single_ac1, type_split='cr',
                amount=200, transaction=tx)

    def test_returns_table_as_expected(self):
        account = self.single_ac1
        table = generate_table(account)

        self.assertEqual(len(table), 4)
        self.assertEqual(table['code'], '1')
