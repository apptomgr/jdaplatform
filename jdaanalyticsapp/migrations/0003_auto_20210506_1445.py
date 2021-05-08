# Generated by Django 3.1.6 on 2021-05-06 18:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('jdaanalyticsapp', '0002_auto_20210502_1156'),
    ]

    operations = [
        migrations.CreateModel(
            name='IndexModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('index', models.CharField(max_length=12)),
            ],
            options={
                'verbose_name_plural': 'IndexModel',
            },
        ),
        migrations.AlterField(
            model_name='securitymodel',
            name='isin',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='indexpricemodel',
            name='index',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jdaanalyticsapp.indexmodel'),
        ),
    ]