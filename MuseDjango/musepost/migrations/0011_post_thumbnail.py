# Generated by Django 3.2.7 on 2022-04-15 00:01

import common.upload_file
import config.asset_storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('musepost', '0010_alter_colorofweek_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='thumbnail',
            field=models.ImageField(blank=True, null=True, storage=config.asset_storage.PublicMediaStorage(), upload_to=common.upload_file.upload_thumbnail_image, verbose_name='썸네일'),
        ),
    ]