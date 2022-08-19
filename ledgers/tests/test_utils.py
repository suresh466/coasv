from django.test import TestCase

from coasc.models import ImpersonalAccount, Split, Transaction

from ledgers.utils import (
        generate_rows, generate_table,
        generate_simple_headers, generate_parent_headers,
        generate_simple_footers, generate_parent_footers,
        get_simple_txs, get_parent_txs,
        generate_simple_rows, generate_parent_rows,
        load_rows_bal, generate_grand_total,
)


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


class GenerateSimpleHeadersTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.single = ImpersonalAccount.objects.create(
                name='single', code=1, type_ac='AS')

    def test_returns_headers_list_as_expected(self):
        acs = ImpersonalAccount.objects.filter(type_ac='AS')
        headers = generate_simple_headers(acs)

        expected_headers = [f'{self.single.name}-{self.single.code}']
        self.assertEqual(headers, expected_headers)

    def test_returns_empty_list_if_no_ac_in_acs(self):
        acs = ImpersonalAccount.objects.filter(type_ac='LI')
        headers = generate_simple_headers(acs)

        expected_headers = []
        self.assertEqual(headers, expected_headers)


class GenerateParentHeadersTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.parent = ImpersonalAccount.objects.create(
                name='parent', code=1, type_ac='EX')
        cls.child = ImpersonalAccount.objects.create(
                name='child', code=1.1, parent_ac=cls.parent)

    def test_returns_headers_list_as_expected(self):
        parent = self.parent
        headers = generate_parent_headers(parent)

        expected_headers = [f'{self.child.name}-{self.child.code}']
        self.assertEqual(headers, expected_headers)

    def test_returns_empty_list_if_no_child_in_parent(self):
        self.child.delete()
        parent = self.parent

        headers = generate_parent_headers(parent)

        expected_headers = []
        self.assertEqual(headers, expected_headers)


class GenerateSimpleFootersTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.single = ImpersonalAccount.objects.create(
                name='single', code=1, type_ac='AS')

    def test_returns_footers_list_as_expected(self):
        acs = ImpersonalAccount.objects.filter(type_ac='AS')
        footers = generate_simple_footers(acs)

        expected_footers = [self.single.current_balance()]
        self.assertEqual(footers, expected_footers)

    def test_returns_empty_list_if_no_child_in_parent(self):
        acs = ImpersonalAccount.objects.filter(type_ac='LI')
        footers = generate_simple_footers(acs)

        expected_footers = []
        self.assertEqual(footers, expected_footers)


class GenerateParentFootersTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.parent = ImpersonalAccount.objects.create(
                name='parent', code=1, type_ac='EX')
        cls.child = ImpersonalAccount.objects.create(
                name='child', code=1.1, parent_ac=cls.parent)

    def test_returns_footers_list_as_expected(self):
        parent = self.parent
        footers = generate_parent_footers(parent)

        expected_footers = [self.child.current_balance()]
        self.assertEqual(footers, expected_footers)

    def test_returns_empty_list_if_no_child_in_parent(self):
        self.child.delete()
        parent = self.parent
        footers = generate_parent_footers(parent)

        expected_footers = []
        self.assertEqual(footers, expected_footers)


class GetSimpleTxsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.single = ImpersonalAccount.objects.create(
                name='single', code='1', type_ac='AS')
        cls.parent = ImpersonalAccount.objects.create(
                name='parent', code='2', type_ac='AS')
        cls.child = ImpersonalAccount.objects.create(
                name='child', code='2.1', parent_ac=cls.parent)
        cls.tx = Transaction.objects.create(description='demo')
        cls.tx1 = Transaction.objects.create(description='demo1')

        Split.objects.create(
                account=cls.single, type_split='dr', amount=1,
                transaction=cls.tx)
        Split.objects.create(
                account=cls.child, type_split='cr', amount=3,
                transaction=cls.tx1)

    def test_returns_txs_list_as_expected(self):
        acs = ImpersonalAccount.objects.filter(type_ac='AS')
        txs = get_simple_txs(acs)

        expected_txs = [self.tx, self.tx1]
        self.assertEqual(txs, expected_txs)

    def test_returns_empty_list_if_no_transactions(self):
        acs = ImpersonalAccount.objects.filter(type_ac='LI')
        txs = get_simple_txs(acs)

        expected_txs = []
        self.assertEqual(txs, expected_txs)


class GetParentTxsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.parent = ImpersonalAccount.objects.create(
                name='parent', code=1, type_ac='EX')
        cls.child = ImpersonalAccount.objects.create(
                name='child', code=1.1, parent_ac=cls.parent)
        cls.tx = Transaction.objects.create(description='demo')
        cls.split = Split.objects.create(
                account=cls.child, type_split='dr', amount=1,
                transaction=cls.tx)

    def test_returns_txs_list_as_expected(self):
        parent = self.parent
        txs = get_parent_txs(parent)

        expected_txs = [self.tx]
        self.assertEqual(txs, expected_txs)

    def test_returns_empty_list_if_no_transactions(self):
        self.split.delete()
        self.tx.delete()
        parent = self.parent

        txs = get_parent_txs(parent)

        expected_txs = []
        self.assertEqual(txs, expected_txs)


class GenerateSimpleRowsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.single = ImpersonalAccount.objects.create(
                name='single', code=1, type_ac='AS')
        cls.tx = Transaction.objects.create(description='demo')
        cls.tx1 = Transaction.objects.create(description='demo1')
        Split.objects.create(
                account=cls.single, type_split='dr', amount=2,
                transaction=cls.tx)
        Split.objects.create(
                account=cls.single, type_split='cr', amount=1,
                transaction=cls.tx)
        Split.objects.create(
                account=cls.single, type_split='cr', amount=1,
                transaction=cls.tx)

        Split.objects.create(
                account=cls.single, type_split='dr', amount=5,
                transaction=cls.tx1)
        Split.objects.create(
                account=cls.single, type_split='cr', amount=2,
                transaction=cls.tx1)

    def test_returns_rows_as_expected(self):
        txs = [self.tx, self.tx1]
        acs = ImpersonalAccount.objects.filter(type_ac='AS')

        rows = generate_simple_rows(txs, acs)

        expected_rows = [
                [{'dr_sum': 2, 'cr_sum': 2, 'diff': 0}],
                [{'dr_sum': 5, 'cr_sum': 2, 'diff': 3}]]
        self.assertEqual(rows, expected_rows)

    def test_returns_empty_list_if_no_transactions(self):
        txs = []
        acs = ImpersonalAccount.objects.filter(type_ac='AS')
        rows = generate_simple_rows(txs, acs)

        expected_rows = []
        self.assertEqual(rows, expected_rows)

    def test_returns_empty_list_of_list_if_no_ac_in_acs(self):
        txs = [self.tx]
        acs = ImpersonalAccount.objects.filter(type_ac='LI')

        rows = generate_simple_rows(txs, acs)

        expected_rows = [[]]
        self.assertEqual(rows, expected_rows)


class GenerateParentRows(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.parent = ImpersonalAccount.objects.create(
                name='parent', code=1, type_ac='EX')
        cls.child = ImpersonalAccount.objects.create(
                name='child', code=1.1, parent_ac=cls.parent)
        cls.tx = Transaction.objects.create(description='demo')
        cls.tx1 = Transaction.objects.create(description='demo1')

        Split.objects.create(
                account=cls.child, type_split='dr', amount=2,
                transaction=cls.tx)
        Split.objects.create(
                account=cls.child, type_split='cr', amount=1,
                transaction=cls.tx)
        Split.objects.create(
                account=cls.child, type_split='cr', amount=1,
                transaction=cls.tx)

        Split.objects.create(
                account=cls.child, type_split='dr', amount=5,
                transaction=cls.tx1)
        Split.objects.create(
                account=cls.child, type_split='cr', amount=2,
                transaction=cls.tx1)

    def test_returns_rows_as_expected(self):
        txs = [self.tx, self.tx1]
        parent = self.parent

        rows = generate_parent_rows(txs, parent)

        expected_rows = [
                [{'dr_sum': 2, 'cr_sum': 2, 'diff': 0}],
                [{'dr_sum': 5, 'cr_sum': 2, 'diff': 3}]]
        self.assertEqual(rows, expected_rows)

    def test_returns_empty_list_if_no_transactions(self):
        txs = []
        parent = self.parent

        rows = generate_parent_rows(txs, parent)

        expected_rows = []
        self.assertEqual(rows, expected_rows)

    def test_returns_empty_list_of_list_if_no_child_in_parent(self):
        Split.objects.all().delete()
        self.tx.delete()
        self.child.delete()

        txs = [self.tx]
        parent = self.parent

        rows = generate_parent_rows(txs, parent)

        expected_rows = [[]]
        self.assertEqual(rows, expected_rows)


class LoadRowsBalTest(TestCase):
    def test_returns_bal_loaded_rows_as_expected(self):
        row = [{'dr_sum': 1, 'cr_sum': 2, 'diff': -1}]
        row1 = [{'dr_sum': 5, 'cr_sum': 2, 'diff': 3}]
        loaded_rows = list(load_rows_bal([row, row1]))

        expected_row = ({'dr_sum': 1, 'cr_sum': 2, 'diff': -1, 'bal': -1},)
        expected_row1 = ({'dr_sum': 5, 'cr_sum': 2, 'diff': 3, 'bal': 2},)
        expected_loaded_rows = [expected_row, expected_row1]

        self.assertEqual(loaded_rows, expected_loaded_rows)

    def test_returns_empty_list_if_no_rows(self):
        loaded_rows = list(load_rows_bal([]))
        expected_loaded_rows = []

        self.assertEqual(loaded_rows, expected_loaded_rows)


class GenerateGrandTotalTest(TestCase):
    def test_returns_grand_total_as_expected(self):
        row = (
                {'dr_sum': 1, 'cr_sum': 2, 'diff': -1, 'bal': -1},
                {'dr_sum': 5, 'cr_sum': 2, 'diff': 3, 'bal': 2}
        )
        bal_loaded_rows = [row]
        grand_total = generate_grand_total(bal_loaded_rows)

        expected_grand_total = [1]
        self.assertEqual(grand_total, expected_grand_total)
