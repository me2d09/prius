# Generated by Django 2.2.2 on 2020-01-10 08:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0042_experiments_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='instrumentgroup',
            name='allowed_LC',
            field=models.ManyToManyField(blank=True, related_name='responsible_for_instrumentgroups', to='app.Contacts'),
        ),
    ]
