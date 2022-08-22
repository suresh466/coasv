from django.test import TestCase
from django.shortcuts import reverse

from coasc.models import ImpersonalAccount


class BalanceSheet(TestCase):
    def test_uses_balance_sheet_template(self):
        ImpersonalAccount(name='single', code=1, type_ac='AS').save()

        response = self.client.get(reverse('fs:balance_sheet'))
        self.assertTemplateUsed(response, 'fs/balance_sheet.html')

    def test_redirects_if_no_acs(self):
        response = self.client.get(reverse('fs:balance_sheet'))
        self.assertRedirects(response, reverse('ledgers:general_ledger'))
