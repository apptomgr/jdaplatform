# Generated by Django 3.1.6 on 2022-04-29 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jdafinancialsapp', '0024_auto_20220429_1056'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exchangemodel',
            name='acronym',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
