# Generated by Django 4.0.6 on 2022-08-07 18:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0011_remove_synctwitteraccount_user_id_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='synctwitteraccount',
            old_name='twitter_id',
            new_name='twitter_name',
        ),
    ]
