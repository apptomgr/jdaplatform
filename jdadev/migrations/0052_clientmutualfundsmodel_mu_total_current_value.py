# Generated by Django 3.2.24 on 2024-07-07 14:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jdadev', '0051_mutualfundmodel_total_current_value'),
    ]

    operations = [
        migrations.AddField(
            model_name='clientmutualfundsmodel',
            name='mu_total_current_value',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=18, null=True),
        ),
    ]