# Generated by Django 2.2 on 2019-04-18 09:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0022_auto_20190410_1628'),
    ]

    operations = [
        migrations.AddField(
            model_name='proposals',
            name='reporter',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='proposal_reporter', to='app.Contacts'),
        ),
    ]