from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium import webdriver
from selenium.webdriver.common.by import By

from coasc.models import ImpersonalAc


class AssetsLedgerTest(StaticLiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()
        ImpersonalAc.objects.create(name='single', code='1', t_ac='AS')

    def tearDown(self):
        self.browser.quit()

    def test_displays_ledger_as_expected(self):
        self.browser.get(f'{self.live_server_url}/ledgers/assets_ledger')
        self.assertIn('Assets Ledger', self.browser.title)

        table = self.browser.find_element(By.TAG_NAME, 'table')
        header = table.find_element(By.TAG_NAME, 'thead')
        footer = table.find_element(By.TAG_NAME, 'tfoot')

        expected_header_text = 'Desc single-1  \n  Dr Cr Bal Grand Total'
        expected_footer_text = 'Total 0 0 0 0'

        self.assertIn(expected_header_text, header.text)
        self.assertIn(expected_footer_text, footer.text)
