# Generated by Django 5.0.3 on 2024-05-27 10:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('balance', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='balance',
            name='date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]