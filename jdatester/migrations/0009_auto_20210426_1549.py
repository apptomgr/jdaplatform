# Generated by Django 3.1.6 on 2021-04-26 19:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jdatester', '0008_auto_20210426_1245'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='securitypricemodel',
            name='ask',
        ),
        migrations.RemoveField(
            model_name='securitypricemodel',
            name='avg_price',
        ),
        migrations.RemoveField(
            model_name='securitypricemodel',
            name='bid',
        ),
        migrations.RemoveField(
            model_name='securitypricemodel',
            name='close',
        ),
        migrations.RemoveField(
            model_name='securitypricemodel',
            name='high',
        ),
        migrations.RemoveField(
            model_name='securitypricemodel',
            name='low',
        ),
        migrations.RemoveField(
            model_name='securitypricemodel',
            name='open',
        ),
        migrations.RemoveField(
            model_name='securitypricemodel',
            name='trans_total',
        ),
        migrations.RemoveField(
            model_name='securitypricemodel',
            name='trans_value',
        ),
        migrations.RemoveField(
            model_name='securitypricemodel',
            name='volume',
        ),
    ]