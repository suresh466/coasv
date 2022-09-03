from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium import webdriver
from selenium.webdriver.common.by import By

from coasc.models import Ac, Split, Transaction


class GeneralLedgerTest(StaticLiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()
        self.single = Ac.objects.create(name='single', code='1', cat='AS')
        self.single1 = Ac.objects.create(name='single1', code='2', cat='LI')

    def tearDown(self):
        self.browser.quit()

    def test_displays_general_ledger_when_no_tx(self):
        # Next day Edith discovered that she can view general ledger
        # of her acs, so she heads over to general ledger page.
        self.browser.get(f'{self.live_server_url}/ledgers/general_ledger/')
        self.assertIn('General Ledger', self.browser.title)

        # She hadn't inputted any txs yet so only her acs
        # are displayed and everything seems to say 0.
        table = self.browser.find_element(By.ID, 'id_single_ledger')
        rows = table.find_elements(By.TAG_NAME, 'tr')
        self.assertIn('single (1)', [row.text for row in rows])
        self.assertIn('Total: 0 0 0', [row.text for row in rows])

        # There is content in the header and footer but nothing in the body.
        self.assertNotIn('desc 0 0 0', [row.text for row in rows])
        table = self.browser.find_element(By.ID, 'id_single1_ledger')
        rows = table.find_elements(By.TAG_NAME, 'tr')
        self.assertIn('single1 (2)', [row.text for row in rows])
        self.assertIn('Total: 0 0 0', [row.text for row in rows])
        self.assertNotIn('desc 0 0 0', [row.text for row in rows])

    def test_displays_general_ledger_when_txs(self):
        # She inputted a few splits, saved the txs and
        # got back to the ledger page.
        tx = Transaction.objects.create(desc='desc')
        Split.objects.create(
                ac=self.single, t_sp='dr',
                am=100, tx=tx)
        Split.objects.create(
                ac=self.single1, t_sp='cr',
                am=100, tx=tx)
        self.browser.get(f'{self.live_server_url}/ledgers/general_ledger/')

        # She notices that tables have interesting header and footer data
        # and discovers that there are different columns for debit and credit
        table = self.browser.find_element(By.ID, 'id_single_ledger')
        rows = table.find_elements(By.TAG_NAME, 'tr')
        self.assertIn('single (1)', [row.text for row in rows])
        self.assertIn('Total: 100.00 0 100.00', [row.text for row in rows])

        # She notices there is content in the body as she expected.
        self.assertIn('desc 100.00 0 100.00', [row.text for row in rows])
        table = self.browser.find_element(By.ID, 'id_single1_ledger')
        rows = table.find_elements(By.TAG_NAME, 'tr')
        self.assertIn('single1 (2)', [row.text for row in rows])
        self.assertIn('Total: 0 100.00 -100.00', [row.text for row in rows])
        self.assertIn('desc 0 100.00 -100.00', [row.text for row in rows])

    def test_displays_message_if_no_acs(self):
        # She just started over by deleting all her acs.
        Ac.objects.all().delete()
        # Curious edith visited general_ledger page to see what would happen.
        self.browser.get(f'{self.live_server_url}/ledgers/general_ledger/')
        body = self.browser.find_element(By.TAG_NAME, 'body')
        self.assertIn(
                'Please create some accounts first; No accounts available',
                body.text)
