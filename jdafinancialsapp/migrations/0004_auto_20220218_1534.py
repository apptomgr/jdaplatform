# Generated by Django 3.1.6 on 2022-02-18 20:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jdafinancialsapp', '0003_auto_20220218_1526'),
    ]

    operations = [
        migrations.RenameField(
            model_name='shareholdermodel',
            old_name='shrhldr_name_1',
            new_name='shrhldr_name',
        ),
        migrations.RenameField(
            model_name='shareholdermodel',
            old_name='shrhldr_type_1',
            new_name='shrhldr_type',
        ),
        migrations.RenameField(
            model_name='shareholdermodel',
            old_name='shrs_hld_1',
            new_name='shrs_hld',
        ),
        migrations.RemoveField(
            model_name='shareholdermodel',
            name='shrhldr_name_2',
        ),
        migrations.RemoveField(
            model_name='shareholdermodel',
            name='shrhldr_name_3',
        ),
        migrations.RemoveField(
            model_name='shareholdermodel',
            name='shrhldr_name_4',
        ),
        migrations.RemoveField(
            model_name='shareholdermodel',
            name='shrhldr_type_2',
        ),
        migrations.RemoveField(
            model_name='shareholdermodel',
            name='shrhldr_type_3',
        ),
        migrations.RemoveField(
            model_name='shareholdermodel',
            name='shrhldr_type_4',
        ),
        migrations.RemoveField(
            model_name='shareholdermodel',
            name='shrs_hld_2',
        ),
        migrations.RemoveField(
            model_name='shareholdermodel',
            name='shrs_hld_3',
        ),
        migrations.RemoveField(
            model_name='shareholdermodel',
            name='shrs_hld_4',
        ),
    ]
