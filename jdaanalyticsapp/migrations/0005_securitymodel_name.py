# Generated by Django 3.1.6 on 2022-02-19 15:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jdaanalyticsapp', '0004_remove_securitymodel_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='securitymodel',
            name='name',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
