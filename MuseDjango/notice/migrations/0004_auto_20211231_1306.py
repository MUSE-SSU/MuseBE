# Generated by Django 3.2.7 on 2021-12-31 13:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notice', '0003_auto_20211231_1304'),
    ]

    operations = [
        migrations.AlterField(
            model_name='banner',
            name='content',
            field=models.TextField(blank=True, max_length=1000, null=True, verbose_name='내용'),
        ),
        migrations.AlterField(
            model_name='banner',
            name='title',
            field=models.TextField(blank=True, max_length=500, null=True, verbose_name='제목'),
        ),
        migrations.AlterField(
            model_name='notice',
            name='title',
            field=models.TextField(blank=True, max_length=500, null=True, verbose_name='제목'),
        ),
    ]