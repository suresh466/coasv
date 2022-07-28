from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver


class someclass(StaticLiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def test_smoke_test(self):
        self.browser.get(f'{self.live_server_url}/data_entry/general_journal/')
        self.assertIn('Coas', self.browser.title)
        self.fail('Finish the test')
