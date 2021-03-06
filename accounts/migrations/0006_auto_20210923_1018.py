# Generated by Django 3.1.6 on 2021-09-23 14:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0012_alter_user_first_name_max_length'),
        ('accounts', '0005_auto_20210521_2259'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='group',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='auth.group'),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='UserGroups',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.group')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
