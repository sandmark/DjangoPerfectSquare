# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-02 16:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
        ('cms', '0005_auto_20170902_1821'),
    ]

    operations = [
        migrations.AddField(
            model_name='content',
            name='sites',
            field=models.ManyToManyField(to='sites.Site'),
        ),
        migrations.AddField(
            model_name='tag',
            name='sites',
            field=models.ManyToManyField(to='sites.Site'),
        ),
    ]
