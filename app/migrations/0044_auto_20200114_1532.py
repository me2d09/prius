# Generated by Django 3.0.2 on 2020-01-14 15:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0043_instrumentgroup_allowed_lc'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='proposals',
            options={'ordering': ('-created',), 'permissions': (('change_status', 'Can set proposal to any status, edit proposal type anytime'), ('approve_technical', 'Can submit technical comments'), ('takeover_panel', 'Can assign a reviewer and submit any review'), ('approve_panel', 'Can submit panel decision'), ('view_panel_proposals', 'Can view panel related proposals'), ('approve_director', 'Can submit director approval'), ('finish_proposal', 'Can finish approved proposal'))},
        ),
    ]
