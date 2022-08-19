from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium import webdriver
from selenium.webdriver.common.by import By

from coasc.models import ImpersonalAccount, Split, Transaction


class LedgerTest(StaticLiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()
        self.single_ac1 = ImpersonalAccount.objects.create(
                name='single_ac1', code='1', type_ac='AS')
        self.single_ac2 = ImpersonalAccount.objects.create(
                name='single_ac2', code='2', type_ac='LI')

    def tearDown(self):
        self.browser.quit()

    def test_displays_ledger_when_no_transaction(self):
        # Edith is exited to checkout ledger of individual her accounts
        self.browser.get(f'{self.live_server_url}/ledgers/ledger/1/')
        self.assertIn('Ledger', self.browser.title)

        # She hadn't inputted any transactions yet so only her account
        # are displayed and everything seems to say 0.
        table = self.browser.find_element(By.ID, 'id_single_ac1_ledger')
        rows = table.find_elements(By.TAG_NAME, 'tr')
        self.assertIn('single_ac1 (1)', [row.text for row in rows])
        self.assertIn('Total: 0 0 0', [row.text for row in rows])
        # There is content in the header and footer but nothing in the body.
        self.assertNotIn('demo desc 0 0 0', [row.text for row in rows])

    def test_displays_ledger_when_transactions(self):
        # She inputted a few splits, saved the transactions and
        # got back to the ledger page.
        tx = Transaction.objects.create(description='demo desc')
        Split.objects.create(
                account=self.single_ac1, type_split='dr',
                amount=100, transaction=tx)
        Split.objects.create(
                account=self.single_ac2, type_split='cr',
                amount=100, transaction=tx)

        # she opened ledger for her single_ac1 first
        self.browser.get(f'{self.live_server_url}/ledgers/ledger/1/')
        # She notices that tables have interesting header and footer data
        # and discovers that there are different columns for debit and credit
        table = self.browser.find_element(By.ID, 'id_single_ac1_ledger')
        rows = table.find_elements(By.TAG_NAME, 'tr')
        self.assertIn('single_ac1 (1)', [row.text for row in rows])
        self.assertIn('Total: 100.00 0 100.00', [row.text for row in rows])
        # She notices there is content in the body as she expected.
        self.assertIn('demo desc 100.00 0 100.00', [row.text for row in rows])

        # Later she also checked out the her second account.
        self.browser.get(f'{self.live_server_url}/ledgers/ledger/2/')
        table = self.browser.find_element(By.ID, 'id_single_ac2_ledger')
        rows = table.find_elements(By.TAG_NAME, 'tr')
        self.assertIn('single_ac2 (2)', [row.text for row in rows])
        self.assertIn('Total: 0 100.00 -100.00', [row.text for row in rows])
        self.assertIn('demo desc 0 100.00 -100.00', [row.text for row in rows])
