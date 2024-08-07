# Generated by Django 3.2.24 on 2024-04-17 21:31

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='StockDailyValuesModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ticker', models.CharField(max_length=100)),
                ('daily_value', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=18, null=True)),
                ('target_value', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=18, null=True)),
            ],
            options={
                'verbose_name_plural': 'StockDailyValuesModel',
            },
        ),
    ]
