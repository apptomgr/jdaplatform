# Generated by Django 3.1.6 on 2022-06-13 00:08

from django.db import migrations
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('jdafinancialsapp', '0075_auto_20220610_0944'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tradepartnersmodel',
            old_name='prtnr_cntry',
            new_name='exp_cntry',
        ),
        migrations.AddField(
            model_name='tradepartnersmodel',
            name='imp_cntry',
            field=django_countries.fields.CountryField(blank=True, max_length=2, null=True),
        ),
    ]
