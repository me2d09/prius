# Generated by Django 2.2.2 on 2019-08-09 15:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0035_auto_20190808_1210'),
    ]

    operations = [
        migrations.AddField(
            model_name='instruments',
            name='starthour',
            field=models.FloatField(blank=True, default=0.0),
        ),
    ]
