# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-19 16:47
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='video',
        ),
        migrations.DeleteModel(
            name='Category',
        ),
    ]