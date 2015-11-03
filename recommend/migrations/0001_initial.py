# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=30, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('city', models.CharField(max_length=50)),
                ('country', models.ForeignKey(to='recommend.Country', related_name='places')),
            ],
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=30, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('places', models.ManyToManyField(to='recommend.Place')),
            ],
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('place', models.ForeignKey(to='recommend.Place')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='votes')),
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
