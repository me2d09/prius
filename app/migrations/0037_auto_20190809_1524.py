# Generated by Django 2.2.2 on 2019-08-09 15:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0036_instruments_starthour'),
    ]

    operations = [
        migrations.RenameField(
            model_name='instruments',
            old_name='starthour',
            new_name='start_hour',
        ),
    ]