# Generated by Django 3.0.5 on 2020-06-12 21:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('classroom', '0027_auto_20200612_2247'),
    ]

    operations = [
        migrations.RenameField(
            model_name='studentanswer',
            old_name='answer_text',
            new_name='answer',
        ),
    ]