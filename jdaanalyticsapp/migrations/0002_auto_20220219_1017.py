# Generated by Django 3.1.6 on 2022-02-19 15:17

from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('jdafinancialsapp', '0006_companymodel_shareholder'),
        ('jdaanalyticsapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExchangeModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=25)),
                ('acronym', models.CharField(max_length=10)),
            ],
            options={
                'verbose_name_plural': 'ExchangeModel',
            },
        ),
        migrations.RemoveField(
            model_name='securitymodel',
            name='name',
        ),
        migrations.AddField(
            model_name='securitymodel',
            name='close_dt',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='securitymodel',
            name='cntry',
            field=django_countries.fields.CountryField(blank=True, max_length=2, null=True),
        ),
        migrations.AddField(
            model_name='securitymodel',
            name='cntry_tax',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='securitymodel',
            name='currency',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='securitymodel',
            name='depsty',
            field=models.CharField(blank=True, choices=[('', 'Depository'), ('Bourse Regionale', 'Bourse Regionale')], max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='securitymodel',
            name='desc',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='securitymodel',
            name='exchg_tax',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='securitymodel',
            name='hghst_appl_rate',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='securitymodel',
            name='instr_type',
            field=models.CharField(blank=True, choices=[('', 'Security Status'), ('Listed', 'Listed'), ('Unquoted', 'Unquoted'), ('Suspended', 'Suspended')], max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='securitymodel',
            name='invstr_cntry_tax',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='securitymodel',
            name='issue',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='jdafinancialsapp.companymodel'),
        ),
        migrations.AddField(
            model_name='securitymodel',
            name='isu_dt',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='securitymodel',
            name='isur_type',
            field=models.CharField(blank=True, choices=[('', 'Issuer Type'), ('Private', 'Private'), ('Public', 'Public')], max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='securitymodel',
            name='listg_sts',
            field=models.CharField(blank=True, choices=[('', 'Listing Status'), ('Listed', 'Listed'), ('Unlisted', 'Unlisted'), ('Suspended', 'Suspended'), ('Deleted', 'Deleted')], max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='securitymodel',
            name='lwst_appl_rate',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='securitymodel',
            name='min_lot',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='securitymodel',
            name='nmnl_amt',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='securitymodel',
            name='open_dt',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='securitymodel',
            name='rgstrr',
            field=models.CharField(blank=True, choices=[('', 'Registrar'), ('Central Bank', 'Central Bank')], max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='securitymodel',
            name='sector',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='jdafinancialsapp.sectormodel'),
        ),
        migrations.AddField(
            model_name='securitymodel',
            name='shr_class',
            field=models.CharField(blank=True, choices=[('', 'Share Class'), ('A', 'A'), ('B', 'B'), ('C', 'C')], max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='securitymodel',
            name='ttl_type',
            field=models.CharField(blank=True, choices=[('', 'Title Type'), ('Listed Share', 'Listed Share'), ('Listed Bond', 'Listed Bond'), ('Unlisted Share', 'Unlisted Share'), ('Unlisted Bond', 'Unlisted Bond')], max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='securitymodel',
            name='txtn_code',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='securitymodel',
            name='val_code',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='StockModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stock_type', models.CharField(max_length=25)),
                ('under_stock_type', models.CharField(max_length=25)),
                ('secr_status', models.CharField(choices=[('', 'Security Status'), ('Listed', 'Listed'), ('Unquoted', 'Unquoted'), ('Suspended', 'Suspended')], max_length=30)),
                ('dvdnd', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('security', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jdaanalyticsapp.securitymodel')),
            ],
            options={
                'verbose_name_plural': 'StockModel',
            },
        ),
        migrations.CreateModel(
            name='BondModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('auth', models.BooleanField()),
                ('security_date', models.DateTimeField()),
                ('gr_bnd_int_rate', models.DecimalField(decimal_places=2, max_digits=10)),
                ('net_bnd_int_rate', models.IntegerField()),
                ('bnd_type', models.CharField(choices=[('', 'Bond Type'), ('Redeemable in Share', 'Redeemable in Share'), ('Constant Redemption Bond', 'Constant Redemption Bond'), ('Deferred Constant Redemption Bond', 'Deferred Constant Redemption Bond'), ('In Fine Bond', 'In Fine Bond')], max_length=50)),
                ('duratn_amt', models.IntegerField()),
                ('duratn_units', models.CharField(choices=[('', 'Duration Units'), ('Monthly', 'Monthyl'), ('Quarterly', 'Quarterly'), ('Semi-annually', 'Semi-annually'), ('Annually', 'Annually')], max_length=50)),
                ('pymt_perd', models.CharField(choices=[('', 'Payment Period'), ('Monthly', 'Monthyl'), ('Quarterly', 'Quarterly'), ('Semi-annually', 'Semi-annually'), ('Annually', 'Annually')], max_length=50)),
                ('pymt_perd_units', models.CharField(choices=[('', 'Payment Period Units'), ('1', '1'), ('5', '5'), ('10', '10'), ('20', '20'), ('30', '30')], max_length=50)),
                ('dfrrd_rpymt_perd_units', models.CharField(choices=[('', 'Deferred Repayment Period Units'), ('0', '1'), ('1', '1'), ('2', '2'), ('3', '3')], max_length=50)),
                ('rpymt_mthd', models.CharField(choices=[('', 'Repayment Method'), ('Sur Valeur', 'Sur Valeur'), ('Sur Valeur', 'Sur Valeur')], max_length=50)),
                ('rpymt_type', models.CharField(choices=[('', 'Repayment Type'), ('Fixed rate', 'Fixed rate'), ('Variable rate', 'Variaible')], max_length=50)),
                ('bnd_isu_dt', models.DateField()),
                ('first_pay_date', models.DateField()),
                ('lst_pay_dt', models.DateField()),
                ('usage', models.IntegerField(choices=[('', 'Usage'), ('360', '360'), ('365', '365')])),
                ('security', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jdaanalyticsapp.securitymodel')),
            ],
            options={
                'verbose_name_plural': 'BondModel',
            },
        ),
        migrations.AddField(
            model_name='securitymodel',
            name='exchg',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='jdaanalyticsapp.exchangemodel'),
        ),
    ]
