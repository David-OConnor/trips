# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recommend', '0002_auto_20151107_1248'),
    ]

    operations = [
        migrations.AlterField(
            model_name='place',
            name='city',
            field=models.CharField(max_length=100),
        ),
    ]
