# Generated by Django 3.1.6 on 2022-06-13 18:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jdafinancialsapp', '0078_auto_20220613_1346'),
    ]

    operations = [
        migrations.AlterField(
            model_name='electionmodel',
            name='elecn_dt',
            field=models.DateField(blank=True, null=True),
        ),
    ]