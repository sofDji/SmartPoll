# Generated by Django 3.0.7 on 2020-06-22 12:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('classroom', '0034_auto_20200620_1946'),
    ]

    operations = [
        migrations.AddField(
            model_name='secret',
            name='ref_quiz',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='ref_quiz', to='classroom.Quiz'),
            preserve_default=False,
        ),
    ]
