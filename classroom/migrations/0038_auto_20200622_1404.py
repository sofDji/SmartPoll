# Generated by Django 3.0.7 on 2020-06-22 13:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('classroom', '0037_secret_ref_quiz'),
    ]

    operations = [
        migrations.AlterField(
            model_name='secret',
            name='ref_quiz',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ref_quiz', to='classroom.Quiz'),
        ),
    ]
