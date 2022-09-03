from django.test import TestCase
from django.urls import reverse

from coasc.models import Ac

from data_entry.views import session_balances


class GeneranJournalViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.single = Ac.objects.create(name='single', cat='AS', code='1')

    def test_uses_general_journal_template(self):
        response = self.client.get(reverse('data_entry:general_journal'))
        self.assertTemplateUsed(response, 'data_entry/general_journal.html')

    def test_redirects_after_POST(self):
        data = {'ac': self.single.pk, 't_sp': 'dr', 'am': '100'}
        url = reverse('data_entry:general_journal')

        response = self.client.post(url, data=data)
        self.assertRedirects(response, url)


class SaveTransactionViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.single = Ac.objects.create(name='single', cat='AS', code='1')
        cls.single1 = Ac.objects.create(name='single1', cat='AS', code='2')

    def populate_splits(self):
        session = self.client.session
        session['splits'] = [
                {'ac': self.single.pk, 't_sp': 'dr', 'am': '100'},
                {'ac': self.single1.pk, 't_sp': 'cr', 'am': '100'}
        ]
        session.save()

    def test_raises_exception_if_splits_is_None(self):
        url = reverse('data_entry:save_transaction')
        data = {'desc': 'desc'}
        message = 'None is not a session split'

        with self.assertRaisesMessage(TypeError, message):
            self.client.post(url, data=data)

    def test_saves_transaction_after_POST(self):
        self.populate_splits()
        url = reverse('data_entry:save_transaction')
        self.client.post(url, {'desc': 'desc'})

        single_bals = self.single.bal()
        single1_bals = self.single1.bal()

        self.assertEqual(single_bals['dr_sum'], 100)
        self.assertEqual(single_bals['cr_sum'], 0)
        self.assertEqual(single1_bals['dr_sum'], 0)
        self.assertEqual(single1_bals['cr_sum'], 100)

    def test_deletes_splits_from_session_after_save(self):
        self.populate_splits()

        url = reverse('data_entry:save_transaction')
        self.client.post(url, {'desc': 'desc'})
        session = self.client.session

        self.assertTrue('splits' not in session)

    def test_redirects_after_POST(self):
        self.populate_splits()

        url = reverse('data_entry:save_transaction')
        data = {'desc': 'desc'}
        response = self.client.post(url, data=data)

        self.assertRedirects(response, reverse('data_entry:general_journal'))


class CancelTransactionViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.single = Ac.objects.create(name='single', cat='AS', code='1')
        cls.single1 = Ac.objects.create(name='single1', cat='AS', code='2')

    def populate_splits(self):
        session = self.client.session
        session['splits'] = [
                {'ac': self.single.pk, 't_sp': 'dr', 'am': '100'},
                {'ac': self.single1.pk, 't_sp': 'cr', 'am': '100'}
        ]

        session.save()

    def test_raises_exception_if_splits_is_None(self):
        message = 'None is not a session split'
        with self.assertRaisesMessage(TypeError, message):
            self.client.post(reverse('data_entry:cancel_transaction'))

    def test_deletes_splits_from_session_after_POST(self):
        self.populate_splits()
        self.client.post(reverse('data_entry:cancel_transaction'))
        session = self.client.session

        self.assertTrue('splits' not in session)

    def test_redirects_after_delete(self):
        self.populate_splits()
        response = self.client.post(reverse('data_entry:cancel_transaction'))
        self.assertRedirects(response, reverse('data_entry:general_journal'))


class SessionBalancesTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.single = Ac.objects.create(name='single', cat='AS', code='1')
        cls.single1 = Ac.objects.create(name='single1', cat='AS', code='2')

    def populate_splits(self):
        session = self.client.session
        session['splits'] = [
                {'ac': self.single.pk, 't_sp': 'dr', 'am': '100'},
                {'ac': self.single1.pk, 't_sp': 'cr', 'am': '50'}
        ]

        session.save()

    def test_session_balances_returns_all_0_if_splits_is_None(self):
        splits = None
        session_bals = session_balances(splits)

        expected_session_bals = {'dr_sum': 0, 'cr_sum': 0, 'diff': 0}
        self.assertEqual(session_bals, expected_session_bals)

    def test_session_balances_returns_correct_values(self):
        self.populate_splits()
        session = self.client.session
        splits = session['splits']

        session_bals = session_balances(splits)

        expected_session_bals = {'dr_sum': 100, 'cr_sum': 50, 'diff': 50}
        self.assertEqual(session_bals, expected_session_bals)
