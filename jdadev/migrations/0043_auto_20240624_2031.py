# Generated by Django 3.2.24 on 2024-06-25 00:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('jdadev', '0042_alter_mutualfundmodel_opcvm'),
    ]

    operations = [
        migrations.CreateModel(
            name='DepositaireModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('depositaire', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='SociateDeGessionModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sociate_de_gession', models.CharField(max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name='clientportfoliomodel',
            name='mutual_funds',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=18, null=True),
        ),
        migrations.CreateModel(
            name='ClientMutualFundsModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('original_value', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=18, null=True)),
                ('current_value', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=18, null=True)),
                ('nbr_of_share', models.IntegerField(blank=True, null=True)),
                ('entry_date', models.DateField(auto_now_add=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('depositaire', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='depositaires', to='jdadev.depositairemodel')),
                ('opcvm', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='opcvms', to='jdadev.bondmodel')),
                ('sociate_de_gession', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sociate_de_gessions', to='jdadev.sociatedegessionmodel')),
            ],
            options={
                'verbose_name_plural': 'ClientMutualFundsModel',
            },
        ),
    ]