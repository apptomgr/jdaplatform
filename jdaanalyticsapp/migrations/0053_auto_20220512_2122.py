# Generated by Django 3.1.6 on 2022-05-13 01:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jdaanalyticsapp', '0052_auto_20220512_2119'),
    ]

    operations = [
        migrations.AlterField(
            model_name='securitymodel',
            name='exchg',
            field=models.ManyToManyField(blank=True, null=True, related_name='exchanges', to='jdaanalyticsapp.ExchangeModel'),
        ),
    ]
