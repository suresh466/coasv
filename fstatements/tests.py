from django.test import TestCase
from django.shortcuts import reverse


class BalanceSheet(TestCase):
    def test_uses_balance_sheet_template(self):
        response = self.client.get(reverse('fs:balance_sheet'))
        self.assertTemplateUsed(response, 'fs/balance_sheet.html')
