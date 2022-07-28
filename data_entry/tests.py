from django.test import TestCase
from django.urls import reverse


class GeneranJournalViewTest(TestCase):
    def test_uses_general_journal_template(self):
        response = self.client.get(reverse('data_entry:general_journal'))
        self.assertTemplateUsed(response, 'data_entry/general_journal.html')
