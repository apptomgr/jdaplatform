# Generated by Django 3.1.6 on 2022-05-17 19:44

from django.db import migrations
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('jdafinancialsapp', '0033_parentcompanymodel_subsidiarymodel'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parentcompanymodel',
            name='cntry',
            field=django_countries.fields.CountryField(blank=True, max_length=2, null=True),
        ),
    ]
