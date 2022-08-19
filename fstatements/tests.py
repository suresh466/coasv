from django.test import TestCase
from django.shortcuts import reverse


class SmokeTest(TestCase):
    def test_smoke_test(self):
        response = self.client.get(reverse('fs:smoke'))
        self.assertEqual(response.status_code, 200)
