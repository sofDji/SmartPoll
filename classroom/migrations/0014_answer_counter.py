# Generated by Django 3.0.5 on 2020-04-23 01:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classroom', '0013_remove_answer_quiz'),
    ]

    operations = [
        migrations.AddField(
            model_name='answer',
            name='counter',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
    ]