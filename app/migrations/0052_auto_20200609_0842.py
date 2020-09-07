# Generated by Django 3.0.6 on 2020-06-09 08:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0051_auto_20200507_1245'),
    ]

    operations = [
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField()),
                ('duration', models.DurationField(editable=False)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='app.Contacts')),
                ('instrument', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='app.Instruments')),
                ('localcontact', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='log_as_lc', to='app.Contacts')),
                ('proposal', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='app.Proposals')),
            ],
            options={
                'ordering': ('-created',),
            },
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300)),
                ('unit', models.CharField(max_length=300)),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.AlterField(
            model_name='publication',
            name='authors',
            field=models.ManyToManyField(blank=True, to='app.Contacts'),
        ),
        migrations.AlterField(
            model_name='publication',
            name='citations',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='publication',
            name='issued',
            field=models.DateField(blank=True, db_index=True, null=True),
        ),
        migrations.CreateModel(
            name='Usage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField()),
                ('log', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='app.Log')),
                ('resource', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='app.Resource')),
            ],
        ),
        migrations.AddField(
            model_name='log',
            name='resources',
            field=models.ManyToManyField(blank=True, through='app.Usage', to='app.Resource'),
        ),
    ]