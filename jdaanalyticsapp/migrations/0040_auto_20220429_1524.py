# Generated by Django 3.1.6 on 2022-04-29 19:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('jdaanalyticsapp', '0039_auto_20220429_1102'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='securitymodel',
            name='exchg',
        ),
        migrations.AddField(
            model_name='exchangemodel',
            name='security',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='jdaanalyticsapp.securitymodel'),
        ),
    ]