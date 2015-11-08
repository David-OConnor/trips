# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Country',
            fields=[
                ('name', models.CharField(unique=True, max_length=100)),
                ('alpha2', models.CharField(unique=True, max_length=2)),
                ('alpha3', models.CharField(primary_key=True, serialize=False, max_length=3)),
            ],
        ),
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('city', models.CharField(max_length=50)),
                ('lat', models.FloatField()),
                ('lon', models.FloatField()),
                ('country', models.ForeignKey(to='recommend.Country', related_name='places')),
            ],
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(unique=True, max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('places', models.ManyToManyField(to='recommend.Place')),
            ],
        ),
        migrations.AddField(
            model_name='country',
            name='region',
            field=models.ForeignKey(to='recommend.Region', related_name='countries'),
        ),
        migrations.AlterUniqueTogether(
            name='place',
            unique_together=set([('city', 'country')]),
        ),
    ]
