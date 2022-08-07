# Generated by Django 4.0.6 on 2022-08-07 17:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0009_synctwitteraccount'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='synctwitteraccount',
            name='user',
        ),
        migrations.AddField(
            model_name='synctwitteraccount',
            name='user_id',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
