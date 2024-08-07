# Generated by Django 3.2.24 on 2024-05-28 12:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jdadev', '0016_rename_total_gain_or_lost_clientequityandrightsmodel_total_gain_or_loss'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bondmodel',
            old_name='ticker',
            new_name='symbol',
        ),
        migrations.AlterField(
            model_name='clientportfoliomodel',
            name='equity_and_rights',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=18, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='bondmodel',
            unique_together={('symbol', 'entry_date')},
        ),
    ]
