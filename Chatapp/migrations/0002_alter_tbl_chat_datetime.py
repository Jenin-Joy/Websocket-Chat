# Generated by Django 5.2 on 2025-05-01 12:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Chatapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tbl_chat',
            name='datetime',
            field=models.DateTimeField(),
        ),
    ]
