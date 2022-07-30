from django.test import TestCase
from django.urls import reverse


class GeneralLedgerViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        pass

    def test_uses_general_ledger_template(self):
        response = self.client.get(reverse('ledgers:general_ledger'))
        self.assertTemplateUsed(response, 'ledgers/general_ledger.html')
