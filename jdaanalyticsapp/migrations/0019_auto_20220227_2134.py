# Generated by Django 3.1.6 on 2022-02-28 02:34

from django.db import migrations
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('jdaanalyticsapp', '0018_auto_20220227_0939'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='securitymodel',
            name='name',
        ),
        migrations.AlterField(
            model_name='securitymodel',
            name='cntry',
            field=django_countries.fields.CountryField(blank=True, max_length=2, null=True),
        ),
    ]
