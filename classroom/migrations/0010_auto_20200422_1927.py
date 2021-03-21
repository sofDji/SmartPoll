# Generated by Django 3.0.5 on 2020-04-22 18:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('classroom', '0009_auto_20200422_1923'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentanswer',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stuanswers', to='classroom.Question'),
        ),
        migrations.AlterField(
            model_name='studentanswer',
            name='quiz',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stuans', to='classroom.Quiz'),
        ),
    ]
