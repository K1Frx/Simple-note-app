# Generated by Django 5.0.1 on 2024-01-20 13:12

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('content', models.TextField()),
                ('public', models.BooleanField(blank=True, default=False)),
                ('encrypted', models.BooleanField(blank=True, default=False)),
                ('password', models.TextField(blank=True, default='')),
                ('user', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notes', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]