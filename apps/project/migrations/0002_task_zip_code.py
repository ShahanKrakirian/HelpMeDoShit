# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-04-26 22:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='zip_code',
            field=models.CharField(default='', max_length=10),
            preserve_default=False,
        ),
    ]