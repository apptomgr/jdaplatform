# Generated by Django 3.1.6 on 2022-03-06 14:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('jdapublicationsapp', '0009_auto_20210707_1726'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prod_name', models.CharField(max_length=250)),
                ('prod_price', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='ProductMetaModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prod_meta_name', models.CharField(max_length=50, verbose_name='Property')),
                ('prod_meta_value', models.CharField(blank=True, max_length=200, null=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jdapublicationsapp.productmodel')),
            ],
        ),
    ]