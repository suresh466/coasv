import time

from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.common.exceptions import WebDriverException

from coasc.models import Ac

MAX_WAIT = 5


class GeneralJournalTest(StaticLiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()
        self.single = Ac.objects.create(name="single", code="1", cat="AS", t_ac="I")
        self.single1 = Ac.objects.create(name="single1", code="2", cat="LI", t_ac="I")

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

    def wait_for_rows_in_table(self, id_table, row_text, assert_in=True):
        start_time = time.time()
        while True:
            try:
                if assert_in:
                    table = self.browser.find_element(By.ID, id_table)
                    rows = table.find_elements(By.TAG_NAME, "tr")
                    self.assertIn(row_text, [row.text for row in rows])
                    return
                table = self.browser.find_element(By.ID, id_table)
                rows = table.find_elements(By.TAG_NAME, "tr")
                self.assertNotIn(row_text, [row.text for row in rows])
                return

            except (AssertionError, WebDriverException) as e:
                if time.time() - start_time > MAX_WAIT:
                    raise e
                time.sleep(0.5)

    def test_can_input_split_display_and_save_it(self):
        # Edith has heard about a new co-operative double entry accounting
        # app. She goes to check the data entry page "general_journal".
        self.browser.get(f"{self.live_server_url}/data_entry/general_journal/")

        # She is immediately invited to input general_journal entries.
        self.select_from_drop_down_id("id_ac", self.single.pk)
        self.select_from_drop_down_id("id_t_sp", "dr")
        self.send_keys_to_inputbox_by_id("id_am", 10)
        self.send_keys_to_inputbox_by_id("id_am", Keys.ENTER)

        # After a redirect the split is visible.
        self.wait_for_rows_in_table("id_dr_splits", "1 dr 10")

        # She proceeds to input another split to balance out the transaction.
        self.select_from_drop_down_id("id_ac", self.single1.pk)
        self.select_from_drop_down_id("id_t_sp", "cr")
        self.send_keys_to_inputbox_by_id("id_am", 10)
        self.send_keys_to_inputbox_by_id("id_am", Keys.ENTER)

        # She is pleased to see both the splits still visible.
        self.wait_for_rows_in_table("id_dr_splits", "1 dr 10")
        self.wait_for_rows_in_table("id_cr_splits", "2 cr 10")

        # She notices that there is a input field below to describe the
        # transaction; she types in "demo desc" and hits enter.
        self.send_keys_to_inputbox_by_id("id_desc", "desc")
        self.send_keys_to_inputbox_by_id("id_desc", Keys.ENTER)

        # The tx is saved and there is no sign of previously visible splits.
        self.wait_for_rows_in_table("id_dr_splits", "1 dr 10", assert_in=False)
        self.wait_for_rows_in_table("id_cr_splits", "2 cr 10", assert_in=False)

    def test_can_cancel_all_session_splits(self):
        self.browser.get(f"{self.live_server_url}/data_entry/general_journal/")

        # The next day edith inputs 2 splits and instantly visible on the page.
        self.select_from_drop_down_id("id_ac", self.single.pk)
        self.select_from_drop_down_id("id_t_sp", "dr")
        self.send_keys_to_inputbox_by_id("id_am", 10)
        self.send_keys_to_inputbox_by_id("id_am", Keys.ENTER)

        time.sleep(1)
        self.select_from_drop_down_id("id_ac", self.single1.pk)
        self.select_from_drop_down_id("id_t_sp", "cr")
        self.send_keys_to_inputbox_by_id("id_am", 10)
        self.send_keys_to_inputbox_by_id("id_am", Keys.ENTER)

        # She is pleased to see both the splits still visible.
        self.wait_for_rows_in_table("id_dr_splits", "1 dr 10")
        self.wait_for_rows_in_table("id_cr_splits", "2 cr 10")

        # but she feels like canceling them, so she clicks on
        # "cancel transaction" button and the splits disappear.
        cancel_transaction = self.browser.find_element(By.ID, "id_cancel_tx")
        ActionChains(self.browser).click(cancel_transaction).perform()

        self.wait_for_rows_in_table("id_dr_splits", "1 dr 10", assert_in=False)
        self.wait_for_rows_in_table("id_cr_splits", "2 cr 10", assert_in=False)

    def test_splits_table_footer_displays_sum_and_difference(self):
        self.browser.get(f"{self.live_server_url}/data_entry/general_journal/")

        # Edith inputs 2 splits.
        self.select_from_drop_down_id("id_ac", self.single.pk)
        self.select_from_drop_down_id("id_t_sp", "dr")
        self.send_keys_to_inputbox_by_id("id_am", 100)
        self.send_keys_to_inputbox_by_id("id_am", Keys.ENTER)

        time.sleep(1)
        self.select_from_drop_down_id("id_ac", self.single1.pk)
        self.select_from_drop_down_id("id_t_sp", "cr")
        self.send_keys_to_inputbox_by_id("id_am", 50)
        self.send_keys_to_inputbox_by_id("id_am", Keys.ENTER)

        # And their sum and difference is visible in table footer.
        self.wait_for_rows_in_table("id_table_splits", "Debit sum: 100 Credit sum: 50")
        self.wait_for_rows_in_table("id_table_splits", "Difference: 50")
