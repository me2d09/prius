# Generated by Django 2.2 on 2019-05-17 16:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0024_auto_20190516_1811'),
    ]

    operations = [
        migrations.AddField(
            model_name='proposals',
            name='grants',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
        migrations.AddField(
            model_name='proposals',
            name='local_contacts',
            field=models.ManyToManyField(blank=True, related_name='proposal_local_contacts', to='app.Contacts'),
        ),
        migrations.AddField(
            model_name='proposals',
            name='thesis_topic',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]
