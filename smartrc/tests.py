import shutil
import tempfile
from pathlib import Path

from django.test import override_settings
from rest_framework.test import APIClient, APITestCase

from balance.models import BillingConfig, UsageTransaction
from .models import NewRc, Rc


class RcApiTests(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        project_root = Path(__file__).resolve().parents[1]
        cls.temp_media_dir = tempfile.mkdtemp()
        shutil.copy(project_root / "media" / "front.png", Path(cls.temp_media_dir) / "front.png")
        shutil.copy(project_root / "media" / "back.png", Path(cls.temp_media_dir) / "back.png")

        cls.settings_override = override_settings(
            MEDIA_ROOT=cls.temp_media_dir,
            FONTS_ROOT=str(project_root / "fonts"),
        )
        cls.settings_override.enable()

    @classmethod
    def tearDownClass(cls):
        cls.settings_override.disable()
        shutil.rmtree(cls.temp_media_dir, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.client = APIClient()
        self.config = BillingConfig.objects.create(
            usage=0,
            limit=100,
            debit_amount=35,
            fetch_amount=5,
            edit_amount=10,
        )

    def new_rc_payload(self, **overrides):
        payload = {
            "rc_type": "New",
            "reg_number": "TN09AB1234",
            "chassis_number": "MCHASSIS123456789012345678",
            "engine_number": "ENG1234567890",
            "name": "Hari Babu",
            "son_of": "Ramakrishnan",
            "street_name": "11 Eswaran Koil Street",
            "city": "Alandur",
            "district": "Chennai",
            "district1": "",
            "reg_date": "18-08-2023",
            "reg_valid": "18-08-2038",
            "fuel": "PETROL",
            "serial": "01",
            "emission_norms": "BS6",
            "issue_date": "18-08-2023",
            "month_year_of_Mfg": "08/2023",
            "number_cylinder": "1",
            "number_of_Axle": "",
            "vehicle_class": "2WN",
            "maker_name": "BAJAJ AUTO LTD",
            "model_name": "PULSAR NS 160",
            "color": "WHITE",
            "body_type": "SOLO",
            "seating": "2",
            "standing": "",
            "sleeper": "",
            "unladen": "153",
            "laden": "303",
            "gross_combination": "",
            "cubic": "160.30",
            "horse_power": "16",
            "wheel_base": "1372",
            "financer": "BAJAJ AUTO FINANCE LTD",
            "rto_name": "MEENAMBAKKAM RTO",
        }
        payload.update(overrides)
        return payload

    def create_existing_new_rc(self, **overrides):
        payload = self.new_rc_payload(**overrides)
        payload.pop("rc_type", None)
        return NewRc.objects.create(**payload)

    def test_create_increases_usage_by_debit_amount(self):
        response = self.client.post("/api/new_create_rc/", self.new_rc_payload(), format="json")

        self.assertEqual(response.status_code, 201)
        self.config.refresh_from_db()
        transaction = UsageTransaction.objects.get(transaction_type=UsageTransaction.RC_CREATE)

        self.assertEqual(self.config.usage, 35)
        self.assertEqual(transaction.amount, 35)
        self.assertEqual(transaction.reg_number, "TN09AB1234")

    def test_create_is_blocked_when_limit_would_be_exceeded(self):
        self.config.usage = 90
        self.config.save()

        response = self.client.post("/api/new_create_rc/", self.new_rc_payload(), format="json")

        self.assertEqual(response.status_code, 400)
        self.config.refresh_from_db()
        self.assertEqual(self.config.usage, 90)
        self.assertFalse(UsageTransaction.objects.filter(transaction_type=UsageTransaction.RC_CREATE).exists())

    def test_edit_increases_usage_by_edit_amount(self):
        self.create_existing_new_rc()

        response = self.client.put(
            "/api/rc/New/TN09AB1234/",
            self.new_rc_payload(name="Hari Babu Updated"),
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.config.refresh_from_db()
        transaction = UsageTransaction.objects.get(transaction_type=UsageTransaction.RC_EDIT)

        self.assertEqual(self.config.usage, 10)
        self.assertEqual(transaction.amount, 10)

    def test_edit_is_blocked_when_limit_would_be_exceeded(self):
        self.create_existing_new_rc()
        self.config.usage = 95
        self.config.save()

        response = self.client.put(
            "/api/rc/New/TN09AB1234/",
            self.new_rc_payload(name="Blocked Edit"),
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.config.refresh_from_db()
        self.assertEqual(self.config.usage, 95)
        self.assertFalse(UsageTransaction.objects.filter(transaction_type=UsageTransaction.RC_EDIT).exists())

    def test_reg_number_cannot_change_during_edit(self):
        self.create_existing_new_rc()

        response = self.client.put(
            "/api/rc/New/TN09AB1234/",
            self.new_rc_payload(reg_number="TN09AB9999"),
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("reg_number", response.data["error"])
        self.assertFalse(UsageTransaction.objects.filter(transaction_type=UsageTransaction.RC_EDIT).exists())

    def test_fetch_reg_detail_does_not_change_usage(self):
        Rc.objects.create(reg_number="TN09AB1234", data={"license_plate": "TN09AB1234"})
        self.config.usage = 22
        self.config.save()

        response = self.client.post(
            "/api/reg_detail/",
            {"reg_number": "TN09AB1234"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.config.refresh_from_db()
        self.assertEqual(self.config.usage, 27)
        self.assertTrue(UsageTransaction.objects.filter(transaction_type=UsageTransaction.RC_FETCH).exists())

    def test_fetch_reg_detail_falls_back_to_saved_rc_record(self):
        self.create_existing_new_rc()

        response = self.client.post(
            "/api/reg_detail/",
            {"reg_number": "tn 09 ab 1234"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["license_plate"], "TN09AB1234")
        self.assertEqual(response.data["owner_name"], "Hari Babu")

    def test_fetch_reg_detail_is_blocked_when_limit_would_be_exceeded(self):
        Rc.objects.create(reg_number="TN09AB1234", data={"license_plate": "TN09AB1234"})
        self.config.usage = 98
        self.config.save()

        response = self.client.post(
            "/api/reg_detail/",
            {"reg_number": "TN09AB1234"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.config.refresh_from_db()
        self.assertEqual(self.config.usage, 98)
