# Generated by Django 5.0.3 on 2024-05-25 07:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('smartrc', '0003_newrc'),
    ]

    operations = [
        migrations.DeleteModel(
            name='BackRcNew',
        ),
        migrations.DeleteModel(
            name='FrontRcNew',
        ),
    ]
