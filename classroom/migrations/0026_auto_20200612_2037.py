# Generated by Django 3.0.5 on 2020-06-12 19:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('classroom', '0025_auto_20200612_1956'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentanswer',
            name='student',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='quiz_answers', to='classroom.Student'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='studentanswer',
            name='question',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='stuanswers', to='classroom.Question'),
        ),
    ]
