# Generated by Django 3.0.5 on 2020-04-22 18:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('classroom', '0010_auto_20200422_1927'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='studentanswer',
            name='question',
        ),
    ]
