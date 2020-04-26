# Generated by Django 2.2.12 on 2020-04-25 08:55

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Meeting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.TextField(blank=True, null=True)),
                ('host_id', models.TextField(blank=True, null=True)),
                ('topic', models.TextField()),
                ('status', models.TextField(blank=True, null=True)),
                ('start_time', models.TextField(blank=True, null=True)),
                ('duration', models.IntegerField()),
                ('timezone', models.TextField(blank=True, null=True)),
                ('agenda', models.TextField(blank=True, null=True)),
                ('created_at', models.TextField(blank=True, null=True)),
                ('start_url', models.TextField(blank=True, null=True)),
                ('join_url', models.TextField(blank=True, null=True)),
                ('zoomus_meeting_id', models.BigIntegerField()),
                ('unit_id', models.IntegerField()),
                ('user_id', models.IntegerField()),
            ],
        ),
    ]
