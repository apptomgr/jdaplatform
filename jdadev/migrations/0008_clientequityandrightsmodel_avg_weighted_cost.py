# Generated by Django 3.2.24 on 2024-05-09 18:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jdadev', '0007_auto_20240506_1517'),
    ]

    operations = [
        migrations.AddField(
            model_name='clientequityandrightsmodel',
            name='avg_weighted_cost',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=18, null=True),
        ),
    ]
