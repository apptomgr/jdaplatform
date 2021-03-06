# Generated by Django 3.1.6 on 2022-04-29 13:46

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('jdafinancialsapp', '0022_auto_20220429_0919'),
    ]

    operations = [
        migrations.AlterField(
            model_name='companymodel',
            name='company',
            field=models.CharField(default=django.utils.timezone.now, max_length=200, unique=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='companymodel',
            name='corp_name',
            field=models.CharField(default=django.utils.timezone.now, max_length=100),
            preserve_default=False,
        ),
    ]
