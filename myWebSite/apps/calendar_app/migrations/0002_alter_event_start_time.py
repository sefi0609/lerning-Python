# Generated by Django 4.1.1 on 2022-10-15 22:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calendar_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='start_time',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]