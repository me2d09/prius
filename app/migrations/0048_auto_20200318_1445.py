# Generated by Django 3.0.4 on 2020-03-18 14:45

import app.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0047_auto_20200318_1439'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='deadline',
            field=models.DateTimeField(default=app.models.default_report_time),
        ),
        migrations.AlterField(
            model_name='report',
            name='year',
            field=models.PositiveIntegerField(default=app.models.current_year),
        ),
    ]
