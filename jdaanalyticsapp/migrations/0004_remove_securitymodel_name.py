# Generated by Django 3.1.6 on 2022-02-19 15:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jdaanalyticsapp', '0003_auto_20220219_1023'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='securitymodel',
            name='name',
        ),
    ]
