# Generated by Django 2.2.7 on 2019-11-29 02:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='disk',
            old_name='iface_type',
            new_name='iface',
        ),
    ]