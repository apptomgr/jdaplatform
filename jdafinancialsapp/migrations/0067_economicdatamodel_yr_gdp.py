# Generated by Django 3.1.6 on 2022-06-06 19:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jdafinancialsapp', '0066_auto_20220606_1420'),
    ]

    operations = [
        migrations.AddField(
            model_name='economicdatamodel',
            name='yr_gdp',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
