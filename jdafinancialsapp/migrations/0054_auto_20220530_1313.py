# Generated by Django 3.1.6 on 2022-05-30 17:13

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('countries_plus', '0005_auto_20160224_1804'),
        ('jdafinancialsapp', '0053_auto_20220530_1307'),
    ]

    operations = [
        migrations.AlterField(
            model_name='countrymodel',
            name='crncy',
            field=models.ForeignKey(default=django.utils.timezone.now, on_delete=django.db.models.deletion.PROTECT, related_name='countries', to='countries_plus.country'),
            preserve_default=False,
        ),
    ]