# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-05-14 13:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0006_vote'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='questions',
            field=models.ManyToManyField(to='questions.Question'),
        ),
    ]
