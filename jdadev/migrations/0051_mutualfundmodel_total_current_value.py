# Generated by Django 3.2.24 on 2024-07-07 14:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jdadev', '0050_auto_20240706_1827'),
    ]

    operations = [
        migrations.AddField(
            model_name='mutualfundmodel',
            name='total_current_value',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=18, null=True),
        ),
    ]
