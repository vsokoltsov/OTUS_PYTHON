# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-05-13 17:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0003_question_tags'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='rate',
            field=models.IntegerField(default=0),
        ),
    ]
