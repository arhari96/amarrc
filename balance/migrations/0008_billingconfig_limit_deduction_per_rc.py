from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("balance", "0007_remove_billingconfig_app_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="billingconfig",
            name="limit_deduction_per_rc",
            field=models.IntegerField(
                default=0,
                help_text="Amount by which the limit decreases each time a brand-new RC is created.",
            ),
        ),
    ]
