# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('subject', models.CharField(max_length=120, verbose_name='Subject')),
                ('body', models.TextField(verbose_name='Body')),
                ('sent_at', models.DateTimeField(null=True, verbose_name='sent at', blank=True)),
                ('read_at', models.DateTimeField(null=True, verbose_name='read at', blank=True)),
                ('replied_at', models.DateTimeField(null=True, verbose_name='replied at', blank=True)),
                ('sender_deleted_at', models.DateTimeField(null=True, verbose_name='Sender deleted at', blank=True)),
                ('recipient_deleted_at', models.DateTimeField(null=True, verbose_name='Recipient deleted at', blank=True)),
                ('parent_msg', models.ForeignKey(null=True, to='django_messages.Message', verbose_name='Parent message', blank=True, related_name='next_messages')),
                ('recipient', models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, verbose_name='Recipient', blank=True, related_name='received_messages')),
                ('sender', models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name='Sender', related_name='sent_messages')),
            ],
            options={
                'ordering': ['-sent_at'],
                'verbose_name_plural': 'Messages',
                'verbose_name': 'Message',
            },
            bases=(models.Model,),
        ),
    ]
