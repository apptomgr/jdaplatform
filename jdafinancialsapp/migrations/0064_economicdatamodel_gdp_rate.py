# Generated by Django 3.1.6 on 2022-06-06 13:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jdafinancialsapp', '0063_economicdatamodel_gdp_amt'),
    ]

    operations = [
        migrations.AddField(
            model_name='economicdatamodel',
            name='gdp_rate',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=18, null=True),
        ),
    ]
