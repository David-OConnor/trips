# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recommend', '0011_auto_20151114_1107'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='country',
            name='tags',
        ),
        migrations.AddField(
            model_name='country',
            name='tags',
            field=models.ManyToManyField(related_name='countries', null=True, to='recommend.CountryTag'),
        ),
    ]
