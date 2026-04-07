# Generated manually for usage-based billing.

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("balance", "0003_balance_recharge_amt"),
    ]

    operations = [
        migrations.CreateModel(
            name="BillingConfig",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("usage", models.IntegerField(default=0)),
                ("limit", models.IntegerField(default=0)),
                ("debit_amount", models.IntegerField(default=0)),
                ("edit_amount", models.IntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Billing Config",
                "verbose_name_plural": "Billing Config",
            },
        ),
        migrations.CreateModel(
            name="UsageTransaction",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "transaction_type",
                    models.CharField(
                        choices=[
                            ("rc_fetch", "RC Fetch"),
                            ("rc_create", "RC Create"),
                            ("rc_edit", "RC Edit"),
                            ("manual_settlement", "Manual Settlement"),
                        ],
                        max_length=32,
                    ),
                ),
                ("amount", models.PositiveIntegerField()),
                ("usage_before", models.IntegerField(default=0)),
                ("usage_after", models.IntegerField(default=0)),
                ("reg_number", models.CharField(blank=True, max_length=10, null=True)),
                ("note", models.CharField(blank=True, max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["-created_at", "-id"],
            },
        ),
    ]
