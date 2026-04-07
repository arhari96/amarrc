from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("balance", "0004_transaction_balance_usage_limit"),
    ]

    operations = [
        migrations.AddField(
            model_name="billingconfig",
            name="fetch_amount",
            field=models.IntegerField(default=0),
        ),
    ]
