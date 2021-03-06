# Generated by Django 3.1.6 on 2022-06-06 19:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jdafinancialsapp', '0068_auto_20220606_1543'),
    ]

    operations = [
        migrations.AlterField(
            model_name='economicdatamodel',
            name='actv_popltn',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=18, null=True),
        ),
        migrations.AlterField(
            model_name='economicdatamodel',
            name='hsehold_cnsmptn',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=18, null=True),
        ),
        migrations.AlterField(
            model_name='economicdatamodel',
            name='ide',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='economicdatamodel',
            name='idh',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=18, null=True),
        ),
        migrations.AlterField(
            model_name='economicdatamodel',
            name='lf_exprn',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=18, null=True),
        ),
        migrations.AlterField(
            model_name='economicdatamodel',
            name='popltn',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=18, null=True),
        ),
        migrations.AlterField(
            model_name='economicdatamodel',
            name='popltn_grth_rate',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=18, null=True),
        ),
        migrations.AlterField(
            model_name='economicdatamodel',
            name='poverty_rate',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=18, null=True),
        ),
        migrations.AlterField(
            model_name='economicdatamodel',
            name='rnkg_bus',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='economicdatamodel',
            name='unemplmt_rate',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=18, null=True),
        ),
    ]
