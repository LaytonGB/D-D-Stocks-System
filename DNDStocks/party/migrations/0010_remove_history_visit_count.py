# Generated by Django 3.1.7 on 2021-03-22 13:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0009_history_visit_count'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='history',
            name='visit_count',
        ),
    ]