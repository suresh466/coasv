# import time

from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
# from selenium.common.exceptions import WebDriverException

from coasc.models import ImpersonalAccount

MAX_WAIT = 5


class GeneralJournalTest(StaticLiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()
        self.single_ac1 = ImpersonalAccount.objects.create(
                name='single_ac1', code='1', type_ac='AS')
        self.single_ac2 = ImpersonalAccount.objects.create(
                name='single_ac2', code='2', type_ac='LI')

    def tearDown(self):
        self.browser.quit()

    def select_from_drop_down_id(self, select_id, option_value):
        select_element = self.browser.find_element(By.ID, select_id)
        select_object = Select(select_element)
        select_object.select_by_value(str(option_value))
        return

    def send_keys_to_inputbox_by_id(self, inputbox_id, input_keys):
        input_box = self.browser.find_element(By.ID, inputbox_id)
        input_box.send_keys(input_keys)
        return

    '''
    def wait_for_rows_in_splits_table(self, row_text):
        start_time = time.time()
        while True:
            try:
                table = self.browser.find_element(By.ID, 'id_splits_table')
                row = table.find_elements(By.TAG_NAME, 'tr')
                self.assertEqual(row.text, row_text)
                return
            except(AssertionError, WebDriverException) as e:
                if(time.time() - start_time > MAX_WAIT):
                    raise e
                time.sleep(0.5)
    '''

    def test_can_input_split_and_display_it(self):
        # Edith has heard about a new co-operative double entry accounting
        # app. She goes to check the data entry page "general_journal".
        self.browser.get(f'{self.live_server_url}/data_entry/general_journal/')

        # She notices that the title says "Coas".
        self.assertIn('Coas', self.browser.title)

        # She is immediately invited to input general_journal entries.
        # She inputs a split.

        self.select_from_drop_down_id('id_account', self.single_ac1.pk)
        self.select_from_drop_down_id('id_type_split', 'dr')
        self.send_keys_to_inputbox_by_id('id_amount', 100)

        page_text = self.browser.find_element(By.TAG_NAME, 'body').text
        self.assertIn('1 dr 100', page_text)
        # After a redirect the split is visible.
        # self.wait_for_rows_in_splits_table('1 dr 100.00')

        self.fail('Finish the test')
