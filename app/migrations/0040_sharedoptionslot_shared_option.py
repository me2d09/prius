# Generated by Django 2.2.2 on 2019-12-16 13:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0039_auto_20191213_1852'),
    ]

    operations = [
        migrations.AddField(
            model_name='sharedoptionslot',
            name='shared_option',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.PROTECT, to='app.SharedOptions'),
        ),
    ]
