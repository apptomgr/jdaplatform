# Generated by Django 3.1.6 on 2021-04-26 21:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jdatester', '0010_securitypricemodel_avg_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='securitypricemodel',
            name='avg_price',
            field=models.FloatField(blank=True, default=0.0, null=True),
        ),
    ]