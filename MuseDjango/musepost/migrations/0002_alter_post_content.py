# Generated by Django 3.2.7 on 2022-01-13 18:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('musepost', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='content',
            field=models.TextField(blank=True, max_length=1000, null=True, verbose_name='내용'),
        ),
    ]
