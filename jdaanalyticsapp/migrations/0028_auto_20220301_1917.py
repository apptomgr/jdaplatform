# Generated by Django 3.1.6 on 2022-03-01 19:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jdaanalyticsapp', '0027_auto_20220228_2213'),
    ]

    operations = [
        migrations.AlterField(
            model_name='securitymodel',
            name='txtn_code',
            field=models.BooleanField(default=True),
            preserve_default=False,
        ),
    ]
