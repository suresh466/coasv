from django.test import TestCase
from django.shortcuts import reverse

from coasc.models import ImpersonalAccount


class TrialBalanceSheetTest(TestCase):
    def test_uses_trial_balance_template(self):
        ImpersonalAccount(name='single', code=1, type_ac='AS').save()
        response = self.client.get(reverse('fs:trial_balance'))
        self.assertTemplateUsed(response, 'fs/trial_balance.html')

    def test_redirects_if_no_acs(self):
        response = self.client.get(reverse('fs:balance_sheet'))
        self.assertRedirects(response, reverse('ledgers:general_ledger'))


class BalanceSheetTest(TestCase):
    def test_uses_balance_sheet_template(self):
        ImpersonalAccount(name='single', code=1, type_ac='AS').save()

        response = self.client.get(reverse('fs:balance_sheet'))
        self.assertTemplateUsed(response, 'fs/balance_sheet.html')

    def test_redirects_if_no_acs(self):
        response = self.client.get(reverse('fs:balance_sheet'))
        self.assertRedirects(response, reverse('ledgers:general_ledger'))


class IncomeStatementTest(TestCase):
    def test_uses_income_statement_template(self):
        ImpersonalAccount(name='parent', code=160, type_ac='AS').save()
        ImpersonalAccount(name='parent', code=150, type_ac='AS').save()

        response = self.client.get(reverse('fs:income_statement'))
        self.assertTemplateUsed(response, 'fs/income_statement.html')

    def test_redirects_if_no_in_ex_ac(self):
        response = self.client.get(reverse('fs:income_statement'))
        self.assertRedirects(response, reverse('ledgers:general_ledger'))
