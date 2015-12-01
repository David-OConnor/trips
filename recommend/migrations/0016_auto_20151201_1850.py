# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recommend', '0015_notfound'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notfound',
            name='count',
            field=models.IntegerField(default=0),
        ),
    ]
