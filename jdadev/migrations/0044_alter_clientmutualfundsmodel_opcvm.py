# Generated by Django 3.2.24 on 2024-06-25 01:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('jdadev', '0043_auto_20240624_2031'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clientmutualfundsmodel',
            name='opcvm',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='opcvms', to='jdadev.mutualfundmodel'),
        ),
    ]