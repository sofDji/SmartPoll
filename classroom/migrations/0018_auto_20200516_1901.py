# Generated by Django 3.0.5 on 2020-05-16 18:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classroom', '0017_auto_20200423_1918'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answer',
            name='counter',
            field=models.FloatField(default=0.0),
        ),
    ]
