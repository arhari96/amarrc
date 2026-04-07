from rest_framework.test import APIClient, APITestCase

from .models import BillingConfig, UsageTransaction


class BillingSummaryTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.config = BillingConfig.objects.create(
            usage=65,
            limit=100,
            debit_amount=35,
            fetch_amount=5,
            edit_amount=10,
        )

    def test_manual_settlement_clamps_usage_to_zero(self):
        UsageTransaction.objects.create(
            transaction_type=UsageTransaction.MANUAL_SETTLEMENT,
            amount=80,
            note="Admin settlement",
        )

        self.config.refresh_from_db()
        transaction = UsageTransaction.objects.get(transaction_type=UsageTransaction.MANUAL_SETTLEMENT)

        self.assertEqual(self.config.usage, 0)
        self.assertEqual(transaction.usage_before, 65)
        self.assertEqual(transaction.usage_after, 0)

    def test_balance_list_returns_usage_summary_shape(self):
        UsageTransaction.objects.create(
            transaction_type=UsageTransaction.RC_CREATE,
            amount=35,
            usage_before=30,
            usage_after=65,
            reg_number="TN09AB1234",
            note="New RC created",
        )

        response = self.client.get("/api/balance_list/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["usage"], 65)
        self.assertEqual(response.data["limit"], 100)
        self.assertEqual(response.data["debit_amount"], 35)
        self.assertEqual(response.data["fetch_amount"], 5)
        self.assertEqual(response.data["edit_amount"], 10)
        self.assertEqual(response.data["remaining_capacity"], 35)
        self.assertTrue(response.data["can_fetch_rc"])
        self.assertTrue(response.data["can_create_rc"])
        self.assertTrue(response.data["can_edit_rc"])
        self.assertEqual(len(response.data["transactions"]), 1)
