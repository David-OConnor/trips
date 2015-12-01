# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recommend', '0013_auto_20151121_1541'),
    ]

    operations = [
        migrations.AlterField(
            model_name='country',
            name='tags',
            field=models.ManyToManyField(related_name='countries', to='recommend.Tag'),
        ),
    ]
