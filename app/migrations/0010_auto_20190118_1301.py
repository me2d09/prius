# Generated by Django 2.1.5 on 2019-01-18 12:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_auto_20190111_1146'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contacts',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
    ]
