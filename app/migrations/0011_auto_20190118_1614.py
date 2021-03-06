# Generated by Django 2.1.5 on 2019-01-18 15:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_auto_20190118_1301'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contacts',
            name='orcid',
            field=models.CharField(blank=True, max_length=40),
        ),
        migrations.AlterField(
            model_name='contacts',
            name='uid',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
    ]
