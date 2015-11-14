# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recommend', '0010_auto_20151114_1054'),
    ]

    operations = [
        migrations.CreateModel(
            name='CountryTag',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.AlterField(
            model_name='country',
            name='subregion',
            field=models.ForeignKey(related_name='countries', to='recommend.Subregion', null=True),
        ),
        migrations.AddField(
            model_name='country',
            name='tags',
            field=models.ForeignKey(related_name='countries', to='recommend.CountryTag', null=True),
        ),
    ]
