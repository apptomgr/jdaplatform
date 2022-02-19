# Generated by Django 3.1.6 on 2022-02-19 20:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('jdaanalyticsapp', '0011_auto_20220219_1523'),
    ]

    operations = [
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
                ('net_bnd_int_rate', models.DecimalField(decimal_places=2, max_digits=10)),
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
    ]