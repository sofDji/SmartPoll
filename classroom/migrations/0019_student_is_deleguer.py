# Generated by Django 3.0.5 on 2020-06-04 16:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classroom', '0018_auto_20200516_1901'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='is_deleguer',
            field=models.BooleanField(default=False),
        ),
    ]
