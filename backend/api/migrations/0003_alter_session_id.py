# Generated by Django 5.1.5 on 2025-01-22 10:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_alter_session_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
