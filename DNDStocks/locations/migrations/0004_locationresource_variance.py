# Generated by Django 3.1.7 on 2021-04-01 18:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0003_auto_20210401_1757'),
    ]

    operations = [
        migrations.AddField(
            model_name='locationresource',
            name='variance',
            field=models.FloatField(default=None, null=True),
        ),
    ]