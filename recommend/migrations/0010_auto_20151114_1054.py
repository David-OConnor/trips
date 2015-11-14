# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recommend', '0009_auto_20151113_2211'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subregion',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(unique=True, max_length=30)),
            ],
        ),
        migrations.AddField(
            model_name='country',
            name='subregion',
            field=models.ForeignKey(null=True, to='recommend.Subregion'),
        ),
    ]
