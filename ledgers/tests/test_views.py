from django.test import TestCase
from django.urls import reverse

from coasc.models import ImpersonalAccount, Split, Transaction


class GeneralLedgerViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.single = ImpersonalAccount.objects.create(
                name='single', code='1', t_ac='AS')
        cls.single1 = ImpersonalAccount.objects.create(
                name='single1', code='2', t_ac='LI')
        cls.parent = ImpersonalAccount.objects.create(
                name='parent', code='3', t_ac='EX')
        cls.child = ImpersonalAccount.objects.create(
                name='child', code='3.1', p_ac=cls.parent)

        tx = Transaction.objects.create(desc='desc')

        Split.objects.create(ac=cls.single, t_sp='dr', am=100, tx=tx)
        Split.objects.create(ac=cls.single1, t_sp='cr', am=100, tx=tx)

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
        cls.single = ImpersonalAccount.objects.create(
                name='single', code='1', t_ac='AS')
        cls.single1 = ImpersonalAccount.objects.create(
                name='single1', code='2', t_ac='LI')

        tx = Transaction.objects.create(desc='desc')

        Split.objects.create(ac=cls.single, t_sp='dr', am=100, tx=tx)
        Split.objects.create(ac=cls.single1, t_sp='cr', am=100, tx=tx)

    def test_uses_ledger_template(self):
        response = self.client.get(reverse('ledgers:ledger', args=[1]))
        self.assertTemplateUsed(response, 'ledgers/ledger.html')

    def test_redirects_if_code_is_None(self):
        response = self.client.get(reverse('ledgers:ledger', args=[None]))
        self.assertRedirects(response, reverse('ledgers:general_ledger'))

    def test_redirects_if_ac_does_not_exist(self):
        response = self.client.get(reverse('ledgers:ledger', args=[3]))
        self.assertRedirects(response, reverse('ledgers:general_ledger'))

    def test_passes_table_to_template_as_expected(self):
        response = self.client.get(reverse('ledgers:ledger', args=[1]))
        table = response.context['table']

        self.assertIn('table', response.context)
        self.assertEqual(table['code'], '1')


class PurchaseViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.parent = ImpersonalAccount.objects.create(
                name='parent', code=150, t_ac='EX')

    def test_uses_purchase_ledger_template(self):
        response = self.client.get(reverse('ledgers:purchase_ledger'))
        self.assertTemplateUsed(response, 'ledgers/purchase_ledger.html')

    def test_returns_message_if_no_parent(self):
        self.parent.delete()

        response = self.client.get(reverse('ledgers:purchase_ledger'))
        self.assertRedirects(response, reverse('ledgers:general_ledger'))


class SalesViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.parent = ImpersonalAccount.objects.create(
                name='parent', code=160, t_ac='EX')

    def test_uses_purchase_ledger_template(self):
        response = self.client.get(reverse('ledgers:sales_ledger'))
        self.assertTemplateUsed(response, 'ledgers/sales_ledger.html')

    def test_redirects_if_no_parent(self):
        self.parent.delete()
        response = self.client.get(reverse('ledgers:sales_ledger'))

        self.assertRedirects(response, reverse('ledgers:general_ledger'))


class AssetsViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.single = ImpersonalAccount.objects.create(
                name='single', code=80, t_ac='AS')
        cls.parent = ImpersonalAccount.objects.create(
                name='parent', code=160, t_ac='AS')

    def test_uses_assets_ledger_template(self):
        response = self.client.get(reverse('ledgers:assets_ledger'))
        self.assertTemplateUsed(response, 'ledgers/assets_ledger.html')

    def test_redirects_if_no_ac_in_acs(self):
        self.single.delete()
        self.parent.delete()

        response = self.client.get(reverse('ledgers:assets_ledger'))

        self.assertRedirects(response, reverse('ledgers:general_ledger'))


class LiabilieitsViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.single = ImpersonalAccount.objects.create(
                name='single', code=10, t_ac='LI')
        cls.parent = ImpersonalAccount.objects.create(
                name='parent', code=20, t_ac='LI')

    def test_uses_liabilities_ledger_template(self):
        response = self.client.get(reverse('ledgers:liabilities_ledger'))
        self.assertTemplateUsed(response, 'ledgers/liabilities_ledger.html')

    def test_redirects_if_no_ac_in_acs(self):
        self.single.delete()
        self.parent.delete()

        response = self.client.get(reverse('ledgers:liabilities_ledger'))

        self.assertRedirects(response, reverse('ledgers:general_ledger'))
