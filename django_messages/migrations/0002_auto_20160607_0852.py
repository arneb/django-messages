# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('django_messages', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='subject',
            field=models.CharField(max_length=140, verbose_name='Subject'),
            preserve_default=True,
        ),
    ]
