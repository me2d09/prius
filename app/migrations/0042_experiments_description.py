# Generated by Django 2.2.2 on 2019-12-17 13:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0041_auto_20191216_1828'),
    ]

    operations = [
        migrations.AddField(
            model_name='experiments',
            name='description',
            field=models.TextField(default='', max_length=5000),
        ),
    ]
