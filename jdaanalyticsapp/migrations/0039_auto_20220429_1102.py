# Generated by Django 3.1.6 on 2022-04-29 15:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jdaanalyticsapp', '0038_auto_20220429_0946'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exchangemodel',
            name='acronym',
            field=models.CharField(blank=True, max_length=225, null=True),
        ),
        migrations.AlterField(
            model_name='exchangemodel',
            name='name',
            field=models.CharField(blank=True, max_length=225, null=True),
        ),
    ]
