# Generated by Django 3.2.24 on 2024-05-28 17:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('jdadev', '0018_clientbondsmodel'),
    ]

    operations = [
        migrations.AddField(
            model_name='clientbondsmodel',
            name='institution_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='institution_types', to='jdadev.bondmodel'),
        ),
    ]
