from coasc.models import Ac, Split, Transaction
from django.test import TestCase
from django.urls import reverse


class GeneralLedgerViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.single = Ac.objects.create(name="single", code="1", cat="AS", t_ac="I")
        cls.single1 = Ac.objects.create(name="single1", code="2", cat="LI", t_ac="I")
        cls.parent = Ac.objects.create(name="parent", code="3", cat="EX", t_ac="I")
        cls.child = Ac.objects.create(name="child", code="3.1", t_ac="I", p_ac=cls.parent)

        tx = Transaction.objects.create(desc="desc")

        Split.objects.create(ac=cls.single, t_sp="dr", am=100, tx=tx)
        Split.objects.create(ac=cls.single1, t_sp="cr", am=100, tx=tx)

    def test_uses_general_ledger_template(self):
        response = self.client.get(reverse("ledgers:general_ledger"))
        self.assertTemplateUsed(response, "ledgers/general_ledger.html")

    def test_passes_tables_to_template_as_expected(self):
        response = self.client.get(reverse("ledgers:general_ledger"))
        tables = response.context["tables"]

        self.assertIn("tables", response.context)
        self.assertEqual(len(tables), 3)
        self.assertEqual(tables[0]["code"], "1")
        self.assertEqual(tables[1]["code"], "2")
        self.assertEqual(tables[2]["code"], "3.1")


class LedgerViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.single = Ac.objects.create(name="single", code="1", cat="AS", t_ac="I")
        cls.single1 = Ac.objects.create(name="single1", code="2", cat="LI", t_ac="I")

        tx = Transaction.objects.create(desc="desc")

        Split.objects.create(ac=cls.single, t_sp="dr", am=100, tx=tx)
        Split.objects.create(ac=cls.single1, t_sp="cr", am=100, tx=tx)

    def test_uses_ledger_template(self):
        response = self.client.get(reverse("ledgers:ledger", args=[1]))
        self.assertTemplateUsed(response, "ledgers/ledger.html")

    def test_passes_table_to_template_as_expected(self):
        response = self.client.get(reverse("ledgers:ledger", args=[1]))
        table = response.context["table"]

        self.assertIn("table", response.context)
        self.assertEqual(table["code"], "1")


class PurchaseViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.parent = Ac.objects.create(name="parent", code=150, cat="EX", t_ac="I")

    def test_uses_purchase_ledger_template(self):
        response = self.client.get(reverse("ledgers:purchase_ledger"))
        self.assertTemplateUsed(response, "ledgers/purchase_ledger.html")


class SalesViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.parent = Ac.objects.create(name="parent", code=160, cat="IN", t_ac="I")

    def test_uses_purchase_ledger_template(self):
        response = self.client.get(reverse("ledgers:sales_ledger"))
        self.assertTemplateUsed(response, "ledgers/sales_ledger.html")


class AssetsViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.single = Ac.objects.create(name="single", code=80, cat="AS", t_ac="I")
        cls.parent = Ac.objects.create(name="parent", code=160, cat="AS", t_ac="I")

    def test_uses_assets_ledger_template(self):
        response = self.client.get(reverse("ledgers:assets_ledger"))
        self.assertTemplateUsed(response, "ledgers/assets_ledger.html")


class LiabilieitsViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.single = Ac.objects.create(name="single", code=10, cat="LI", t_ac="I")
        cls.parent = Ac.objects.create(name="parent", code=20, cat="LI", t_ac="I")

    def test_uses_liabilities_ledger_template(self):
        response = self.client.get(reverse("ledgers:liabilities_ledger"))
        self.assertTemplateUsed(response, "ledgers/liabilities_ledger.html")
