# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recommend', '0005_submission_test'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='submission',
            name='places',
        ),
        migrations.DeleteModel(
            name='Submission',
        ),
    ]
