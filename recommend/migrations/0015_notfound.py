# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recommend', '0014_auto_20151125_1732'),
    ]

    operations = [
        migrations.CreateModel(
            name='NotFound',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('count', models.IntegerField()),
            ],
        ),
    ]
