# Generated by Django 3.2.7 on 2021-12-31 14:29

from django.db import migrations
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0003_taggeditem_add_unique_index'),
        ('musepost', '0043_auto_20211231_1404'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='taggedpost',
            name='post',
        ),
        migrations.RemoveField(
            model_name='taggedpost',
            name='tag',
        ),
        migrations.RemoveField(
            model_name='taggedpost',
            name='tags',
        ),
        migrations.AlterField(
            model_name='post',
            name='hashtag',
            field=taggit.managers.TaggableManager(blank=True, help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
        migrations.DeleteModel(
            name='Tag',
        ),
        migrations.DeleteModel(
            name='TaggedPost',
        ),
    ]
