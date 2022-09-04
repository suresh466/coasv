from django.test import TestCase

from coasc.models import Ac, Split, Transaction

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
        cls.single = Ac.objects.create(
                name='single', code='1', cat='AS', t_ac='I')

        tx = Transaction.objects.create(desc='desc')

        Split.objects.create(ac=cls.single, t_sp='dr', am=100, tx=tx)
        Split.objects.create(ac=cls.single, t_sp='cr', am=200, tx=tx)

    def test_returns_emtpy_list_if_no_splits(self):
        sps = []
        rows = generate_rows(sps)

        self.assertFalse(rows)

    def test_returns_rows_as_expected(self):
        sps = self.single.split_set.all()
        rows = generate_rows(sps)

        row1 = {'debit': 100.00, 'credit': 0, 'diff': 100.00, 'desc': 'desc'}
        row2 = {'debit': 0, 'credit': 200.00, 'diff': -100.00, 'desc': 'desc'}
        expected_rows = [row1, row2]

        self.assertEqual(len(rows), 2)
        self.assertEqual(rows, expected_rows)


class GenerateTableTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.single = Ac.objects.create(
                name='single', code='1', cat='AS', t_ac='I')

        tx = Transaction.objects.create(desc='desc')

        Split.objects.create(ac=cls.single, t_sp='dr', am=100, tx=tx)
        Split.objects.create(ac=cls.single, t_sp='cr', am=200, tx=tx)

    def test_returns_table_as_expected(self):
        ac = self.single
        table = generate_table(ac)

        self.assertEqual(len(table), 4)
        self.assertEqual(table['code'], '1')


class GenerateSimpleHeadersTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.single = Ac.objects.create(
                name='single', code=1, cat='AS', t_ac='I')

    def test_returns_headers_list_as_expected(self):
        acs = Ac.objects.filter(cat='AS')

        headers = generate_simple_headers(acs)
        expected_headers = [f'{self.single.name}-{self.single.code}']

        self.assertEqual(headers, expected_headers)

    def test_returns_empty_list_if_no_ac_in_acs(self):
        acs = Ac.objects.filter(cat='LI')

        headers = generate_simple_headers(acs)
        expected_headers = []

        self.assertEqual(headers, expected_headers)


class GenerateParentHeadersTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.parent = Ac.objects.create(
                name='parent', code=1, cat='EX', t_ac='I')
        cls.child = Ac.objects.create(
                name='child', code=1.1, t_ac='I', p_ac=cls.parent)

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
        cls.single = Ac.objects.create(
                name='single', code=1, cat='AS', t_ac='I')

    def test_returns_footers_list_as_expected(self):
        acs = Ac.objects.filter(cat='AS')

        footers = generate_simple_footers(acs)
        expected_footers = [self.single.bal()]

        self.assertEqual(footers, expected_footers)

    def test_returns_empty_list_if_no_child_in_parent(self):
        acs = Ac.objects.filter(cat='LI')

        footers = generate_simple_footers(acs)
        expected_footers = []

        self.assertEqual(footers, expected_footers)


class GenerateParentFootersTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.parent = Ac.objects.create(
                name='parent', code=1, cat='EX', t_ac='I')
        cls.child = Ac.objects.create(
                name='child', code=1.1, t_ac='I', p_ac=cls.parent)

    def test_returns_footers_list_as_expected(self):
        footers = generate_parent_footers(self.parent)
        expected_footers = [self.child.bal()]

        self.assertEqual(footers, expected_footers)

    def test_returns_empty_list_if_no_child_in_parent(self):
        self.child.delete()

        footers = generate_parent_footers(self.parent)
        expected_footers = []

        self.assertEqual(footers, expected_footers)


class GetSimpleTxsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.single = Ac.objects.create(
                name='single', code='1', cat='AS', t_ac='I')
        cls.parent = Ac.objects.create(
                name='parent', code='2', cat='AS', t_ac='I')
        cls.child = Ac.objects.create(
                name='child', code='2.1', t_ac='I', p_ac=cls.parent)

        cls.tx = Transaction.objects.create(desc='desc')
        cls.tx1 = Transaction.objects.create(desc='desc1')

        Split.objects.create(ac=cls.single, t_sp='dr', am=1, tx=cls.tx)
        Split.objects.create(ac=cls.child, t_sp='cr', am=3, tx=cls.tx1)

    def test_returns_txs_list_as_expected(self):
        acs = Ac.objects.filter(cat='AS')

        txs = get_simple_txs(acs)
        expected_txs = [self.tx, self.tx1]

        self.assertEqual(txs, expected_txs)

    def test_returns_empty_list_if_no_txs(self):
        acs = Ac.objects.filter(cat='LI')

        txs = get_simple_txs(acs)
        expected_txs = []

        self.assertEqual(txs, expected_txs)


class GetParentTxsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.parent = Ac.objects.create(
                name='parent', code=1, cat='EX', t_ac='I')
        cls.child = Ac.objects.create(
                name='child', code=1.1, t_ac='I', p_ac=cls.parent)

        cls.tx = Transaction.objects.create(desc='desc')

        cls.sp = Split.objects.create(ac=cls.child, t_sp='dr', am=1, tx=cls.tx)

    def test_returns_txs_list_as_expected(self):
        txs = get_parent_txs(self.parent)
        expected_txs = [self.tx]

        self.assertEqual(txs, expected_txs)

    def test_returns_empty_list_if_no_txs(self):
        self.sp.delete()
        self.tx.delete()

        txs = get_parent_txs(self.parent)
        expected_txs = []

        self.assertEqual(txs, expected_txs)


class GenerateSimpleRowsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.single = Ac.objects.create(
                name='single', code=1, cat='AS', t_ac='I')

        cls.tx = Transaction.objects.create(desc='desc')
        cls.tx1 = Transaction.objects.create(desc='desc1')

        Split.objects.create(ac=cls.single, t_sp='dr', am=2, tx=cls.tx)
        Split.objects.create(ac=cls.single, t_sp='cr', am=1, tx=cls.tx)
        Split.objects.create(ac=cls.single, t_sp='cr', am=1, tx=cls.tx)

        Split.objects.create(ac=cls.single, t_sp='dr', am=5, tx=cls.tx1)
        Split.objects.create(ac=cls.single, t_sp='cr', am=2, tx=cls.tx1)

    def test_returns_rows_as_expected(self):
        txs = [self.tx, self.tx1]
        acs = Ac.objects.filter(cat='AS')

        rows = generate_simple_rows(txs, acs)
        expected_rows = [
                [{'dr_sum': 2, 'cr_sum': 2, 'diff': 0}],
                [{'dr_sum': 5, 'cr_sum': 2, 'diff': 3}]]

        self.assertEqual(rows, expected_rows)

    def test_returns_empty_list_if_no_txs(self):
        txs = []
        acs = Ac.objects.filter(cat='AS')

        rows = generate_simple_rows(txs, acs)
        expected_rows = []

        self.assertEqual(rows, expected_rows)

    def test_returns_empty_list_of_list_if_no_ac_in_acs(self):
        txs = [self.tx]
        acs = Ac.objects.filter(cat='LI')

        rows = generate_simple_rows(txs, acs)
        expected_rows = [[]]

        self.assertEqual(rows, expected_rows)


class GenerateParentRows(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.parent = Ac.objects.create(
                name='parent', code=1, cat='EX', t_ac='I')
        cls.child = Ac.objects.create(
                name='child', code=1.1, t_ac='I', p_ac=cls.parent)

        cls.tx = Transaction.objects.create(desc='desc')
        cls.tx1 = Transaction.objects.create(desc='desc1')

        Split.objects.create(ac=cls.child, t_sp='dr', am=2, tx=cls.tx)
        Split.objects.create(ac=cls.child, t_sp='cr', am=1, tx=cls.tx)
        Split.objects.create(ac=cls.child, t_sp='cr', am=1, tx=cls.tx)

        Split.objects.create(ac=cls.child, t_sp='dr', am=5, tx=cls.tx1)
        Split.objects.create(ac=cls.child, t_sp='cr', am=2, tx=cls.tx1)

    def test_returns_rows_as_expected(self):
        txs = [self.tx, self.tx1]
        parent = self.parent

        rows = generate_parent_rows(txs, parent)
        expected_rows = [
                [{'dr_sum': 2, 'cr_sum': 2, 'diff': 0}],
                [{'dr_sum': 5, 'cr_sum': 2, 'diff': 3}]]

        self.assertEqual(rows, expected_rows)

    def test_returns_empty_list_if_no_txs(self):
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
