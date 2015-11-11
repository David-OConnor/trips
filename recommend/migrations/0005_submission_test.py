# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recommend', '0004_auto_20151107_1301'),
    ]

    operations = [
        migrations.AddField(
            model_name='submission',
            name='test',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
