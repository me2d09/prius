# Generated by Django 2.2 on 2019-05-16 16:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0023_proposals_reporter'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='proposals',
            options={'ordering': ('-created',), 'permissions': (('change_status', 'Can set proposal to any status, edit proposal type anytime'), ('approve_technical', 'Can submit technical comments'), ('takeover_panel', 'Can assign a reviewer and submit any review'), ('approve_panel', 'Can submit panel decision'), ('approve_director', 'Can submit director approval'), ('finish_proposal', 'Can finish approved proposal'))},
        ),
    ]
