# Generated by Django 5.1.3 on 2024-12-21 03:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('phone_number', models.CharField(blank=True, max_length=15, null=True)),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('google_id', models.CharField(blank=True, max_length=100, null=True, unique=True)),
                ('apple_id', models.CharField(blank=True, max_length=100, null=True, unique=True)),
                ('auth_type', models.CharField(blank=True, max_length=30, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'users',
            },
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('device_name', models.CharField(help_text='Name of the device used for the session', max_length=100)),
                ('token', models.CharField(help_text='Session token', max_length=255, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='The time when the session was created')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='The time when the session was last updated')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sessions', to='auth_micro.user')),
            ],
            options={
                'db_table': 'sessions',
            },
        ),
    ]
