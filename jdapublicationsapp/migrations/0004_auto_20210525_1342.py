# Generated by Django 3.1.6 on 2021-05-25 17:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jdapublicationsapp', '0003_publicationmodel_tmp_file_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='publicationmodel',
            old_name='tmp_file_name',
            new_name='tmp_pdf_file',
        ),
    ]