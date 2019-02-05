# Generated by Django 2.1.4 on 2018-12-04 15:45

from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_auto_20181204_1640'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proposals',
            name='continuation',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='proposal_continuation', to='app.Proposals'),
        ),
        migrations.AlterField(
            model_name='proposals',
            name='coproposers',
            field=models.ManyToManyField(blank=True, null=True, related_name='proposal_coporposals', to='app.Contacts'),
        ),
        migrations.AlterField(
            model_name='proposals',
            name='publications',
            field=models.ManyToManyField(blank=True, null=True, to='app.Publications'),
        ),
        migrations.AlterField(
            model_name='proposals',
            name='resubmission',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='app.Proposals'),
        ),
        migrations.AlterField(
            model_name='proposals',
            name='samples',
            field=models.ManyToManyField(blank=True, null=True, to='app.Samples'),
        ),
        migrations.AlterField(
            model_name='proposals',
            name='scientific_bg',
            field=models.FileField(blank=True, null=True, upload_to='.'),
        ),
        migrations.AlterField(
            model_name='proposals',
            name='slug',
            field=django_extensions.db.fields.AutoSlugField(blank=True, editable=False, null=True, populate_from='name'),
        ),
    ]
