# Generated by Django 3.1.6 on 2022-03-09 01:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jdafinancialsapp', '0011_productmetamodel_productmodel'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ProductMetaModel',
        ),
        migrations.DeleteModel(
            name='ProductModel',
        ),
    ]
