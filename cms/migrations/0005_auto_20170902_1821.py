# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-02 09:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
        ('cms', '0004_auto_20170821_0804'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(max_length=255, unique=True, verbose_name='名前'),
        ),
    ]
