# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-26 00:54
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('klimr_main', '0008_auto_20170423_1406'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupsemesterstate',
            name='praepostor',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='klimr_main.Student'),
        ),
    ]
