# Generated by Django 2.2 on 2019-05-17 16:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0026_auto_20190517_1844'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='proposals',
            name='local_contact',
        ),
    ]
