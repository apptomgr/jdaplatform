# Generated by Django 3.1.6 on 2022-02-18 20:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('jdafinancialsapp', '0005_remove_companymodel_shareholder'),
    ]

    operations = [
        migrations.AddField(
            model_name='companymodel',
            name='shareholder',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='jdafinancialsapp.shareholdermodel'),
        ),
    ]
