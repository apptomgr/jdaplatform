# Generated by Django 3.1.6 on 2022-05-30 16:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jdafinancialsapp', '0046_auto_20220530_1118'),
    ]

    operations = [
        migrations.AlterField(
            model_name='countrymodel',
            name='crncy',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
