# Generated by Django 3.1.6 on 2022-04-20 23:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jdaanalyticsapp', '0034_auto_20220419_1950'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bondmodel',
            old_name='isu_dt',
            new_name='bnd_isu_dt',
        ),
    ]