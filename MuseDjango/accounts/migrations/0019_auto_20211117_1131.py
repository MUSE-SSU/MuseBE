# Generated by Django 3.2.7 on 2021-11-17 11:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0018_auto_20211117_1129'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='follow',
            options={'verbose_name_plural': '팔로우'},
        ),
        migrations.AlterModelOptions(
            name='user',
            options={'verbose_name_plural': '유저'},
        ),
        migrations.AlterModelOptions(
            name='userprofile',
            options={'verbose_name_plural': '유저 프로필'},
        ),
    ]
