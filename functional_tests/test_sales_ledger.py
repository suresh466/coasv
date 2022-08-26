from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium import webdriver
from selenium.webdriver.common.by import By

from coasc.models import ImpersonalAccount


class SalesLedgerTest(StaticLiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()
        self.parent = ImpersonalAccount.objects.create(
                name='parent', code=160, t_ac='EX')
        ImpersonalAccount.objects.create(
                name='child', code=160.1, p_ac=self.parent)

    def tearDown(self):
        self.browser.quit()

    def test_displays_ledger_as_expected(self):
        self.browser.get(f'{self.live_server_url}/ledgers/sales_ledger')
        self.assertIn('Sales Ledger', self.browser.title)

        table = self.browser.find_element(By.TAG_NAME, 'table')
        header = table.find_element(By.TAG_NAME, 'thead')
        footer = table.find_element(By.TAG_NAME, 'tfoot')

        expected_header_text = 'Desc child-160.1 Total Inc'
        expected_footer_text = 'Total 0 0'

        self.assertIn(expected_header_text, header.text)
        self.assertIn(expected_footer_text, footer.text)
