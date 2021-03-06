# Generated by Django 3.1.6 on 2022-06-10 13:10

from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('jdafinancialsapp', '0072_otherindicatorsmodel'),
    ]

    operations = [
        migrations.CreateModel(
            name='BusinessPartnersModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('yr', models.IntegerField(blank=True, null=True)),
                ('prtnr_cntry', django_countries.fields.CountryField(blank=True, max_length=2, null=True)),
                ('imp_exp_code', models.CharField(blank=True, max_length=1, null=True)),
                ('imp_exp_amt', models.DecimalField(blank=True, decimal_places=2, max_digits=18, null=True)),
                ('country', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='business_partners', to='jdafinancialsapp.countrymodel')),
            ],
            options={
                'verbose_name_plural': 'BusinessPartnersModel',
                'db_table': 'BusinessPartnersModel',
            },
        ),
    ]
