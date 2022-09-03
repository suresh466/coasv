from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium import webdriver
from selenium.webdriver.common.by import By

from coasc.models import Ac


class PurchaseLedgerViewTest(StaticLiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()
        self.parent = Ac.objects.create(name='parent', code=150, cat='EX')
        Ac.objects.create(name='child', code=150.1, p_ac=self.parent)

    def tearDown(self):
        self.browser.quit()

    def test_displays_ledger_as_expected(self):
        self.browser.get(f'{self.live_server_url}/ledgers/purchase_ledger')
        self.assertIn('Purchase Ledger', self.browser.title)

        table = self.browser.find_element(By.TAG_NAME, 'table')
        header = table.find_element(By.TAG_NAME, 'thead')
        footer = table.find_element(By.TAG_NAME, 'tfoot')

        expected_header_text = 'Desc child-150.1 Total Exp'
        expected_footer_text = 'Total 0 0'

        self.assertIn(expected_header_text, header.text)
        self.assertIn(expected_footer_text, footer.text)
