# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recommend', '0007_submission'),
    ]

    operations = [
        migrations.AddField(
            model_name='country',
            name='alternate_names',
            field=models.TextField(null=True),
        ),
    ]
