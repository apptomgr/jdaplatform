# Generated by Django 3.1.6 on 2022-06-06 00:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jdafinancialsapp', '0062_auto_20220605_2005'),
    ]

    operations = [
        migrations.AddField(
            model_name='economicdatamodel',
            name='gdp_amt',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
