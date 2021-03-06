# Generated by Django 2.1.7 on 2019-04-09 15:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0020_contacts_description'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='proposals',
            options={'ordering': ('-created',), 'permissions': (('change_status', 'Can set proposal to any status, edit proposal type anytime'), ('approve_technical', 'Can submit technical comments'), ('takeover_panel', 'Can put proposal to review'), ('approve_panel', 'Can submit panel decision'), ('approve_director', 'Can submit director approval'), ('finish_proposal', 'Can finish approved proposal'))},
        ),
    ]
