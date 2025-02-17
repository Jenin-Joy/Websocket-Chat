# Generated by Django 5.1.3 on 2024-11-27 07:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Guest', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='tbl_chat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(max_length=500)),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('reciver_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reciver_id', to='Guest.tbl_user')),
                ('sender_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sender_id', to='Guest.tbl_user')),
            ],
        ),
    ]
