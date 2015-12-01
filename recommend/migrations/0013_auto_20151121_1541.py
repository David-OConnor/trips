# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recommend', '0012_auto_20151114_1724'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CountryTag',
        ),
        migrations.AlterField(
            model_name='country',
            name='tags',
            field=models.ManyToManyField(related_name='countries', null=True, to='recommend.Tag'),
        ),
    ]
