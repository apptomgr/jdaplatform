# Generated by Django 3.2.24 on 2024-05-20 02:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('jdadev', '0011_rename_current_price_clientequityandrightsmodel_daily_value'),
    ]

    operations = [
        migrations.CreateModel(
            name='Daily_stock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stock', models.CharField(max_length=100)),
                ('daily_price', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='Client_portfolio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number_of_stocks', models.PositiveIntegerField()),
                ('total_value', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jdadev.daily_stock')),
            ],
        ),
    ]
