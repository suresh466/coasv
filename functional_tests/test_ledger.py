from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium import webdriver
from selenium.webdriver.common.by import By

from coasc.models import Ac, Split, Transaction


class LedgerTest(StaticLiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()
        self.single = Ac.objects.create(name='single', code='1', cat='AS')
        self.single1 = Ac.objects.create(name='single1', code='2', cat='LI')

    def tearDown(self):
        self.browser.quit()

    def test_displays_ledger_when_no_tx(self):
        # Edith is exited to checkout ledger of individual her acs
        self.browser.get(f'{self.live_server_url}/ledgers/ledger/1/')
        self.assertIn('Ledger', self.browser.title)

        # She hadn't inputted any txs yet so only her ac
        # are displayed and everything seems to say 0.
        table = self.browser.find_element(By.ID, 'id_single_ledger')
        rows = table.find_elements(By.TAG_NAME, 'tr')
        self.assertIn('single (1)', [row.text for row in rows])
        self.assertIn('Total: 0 0 0', [row.text for row in rows])
        # There is content in the header and footer but nothing in the body.
        self.assertNotIn('desc 0 0 0', [row.text for row in rows])

    def test_displays_ledger_when_txs(self):
        # She inputted a few splits, saved the txs and
        # got back to the ledger page.
        tx = Transaction.objects.create(desc='desc')
        Split.objects.create(
                ac=self.single, t_sp='dr',
                am=100, tx=tx)
        Split.objects.create(
                ac=self.single1, t_sp='cr',
                am=100, tx=tx)

        # she opened ledger for her single first
        self.browser.get(f'{self.live_server_url}/ledgers/ledger/1/')
        # She notices that tables have interesting header and footer data
        # and discovers that there are different columns for debit and credit
        table = self.browser.find_element(By.ID, 'id_single_ledger')
        rows = table.find_elements(By.TAG_NAME, 'tr')
        self.assertIn('single (1)', [row.text for row in rows])
        self.assertIn('Total: 100.00 0 100.00', [row.text for row in rows])
        # She notices there is content in the body as she expected.
        self.assertIn('desc 100.00 0 100.00', [row.text for row in rows])

        # Later she also checked out the her second ac.
        self.browser.get(f'{self.live_server_url}/ledgers/ledger/2/')
        table = self.browser.find_element(By.ID, 'id_single1_ledger')
        rows = table.find_elements(By.TAG_NAME, 'tr')
        self.assertIn('single1 (2)', [row.text for row in rows])
        self.assertIn('Total: 0 100.00 -100.00', [row.text for row in rows])
        self.assertIn('desc 0 100.00 -100.00', [row.text for row in rows])
