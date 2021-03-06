# Generated by Django 3.2.7 on 2022-01-27 19:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('topics', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='topic',
            name='activate_week',
            field=models.BooleanField(default=True, verbose_name='현재 진행 주차'),
        ),
        migrations.AlterField(
            model_name='topic',
            name='topic',
            field=models.CharField(default='자유', max_length=128, verbose_name='주제'),
        ),
    ]
