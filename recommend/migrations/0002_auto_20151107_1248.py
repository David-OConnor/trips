# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recommend', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='place',
            name='division_code',
            field=models.IntegerField(default=999),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='place',
            unique_together=set([('city', 'country', 'division_code')]),
        ),
    ]
