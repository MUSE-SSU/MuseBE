# Generated by Django 3.2.7 on 2022-01-06 03:35

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Banner',
            fields=[
                ('idx', models.AutoField(primary_key=True, serialize=False)),
                ('category', models.CharField(blank=True, choices=[('main', '메인 배너'), ('muse', '뮤즈 배너'), ('contest', '콘테스트 배너'), ('reference', '레퍼런스 배너')], max_length=30, null=True, verbose_name='배너 카테고리')),
                ('title', models.TextField(blank=True, max_length=500, null=True, verbose_name='제목')),
                ('content', models.TextField(blank=True, max_length=1000, null=True, verbose_name='내용')),
                ('usage', models.BooleanField(default=True, verbose_name='노출 여부')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='최초 업로드 날짜')),
                ('modified_at', models.DateTimeField(auto_now=True, verbose_name='최근 수정 날짜')),
            ],
            options={
                'verbose_name_plural': '배너',
                'db_table': 'MUSE_Banner',
            },
        ),
        migrations.CreateModel(
            name='Notice',
            fields=[
                ('idx', models.AutoField(primary_key=True, serialize=False)),
                ('category', models.CharField(blank=True, choices=[('tos', '이용 약관'), ('guide', '이용 안내'), ('footer', '사이트 하단 설명'), ('popup', '일회성 팝업')], max_length=30, null=True, verbose_name='공지 카테고리')),
                ('title', models.TextField(blank=True, max_length=500, null=True, verbose_name='제목')),
                ('content', models.TextField(blank=True, max_length=1000, null=True, verbose_name='내용')),
                ('usage', models.BooleanField(default=True, verbose_name='노출 여부')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='최초 업로드 날짜')),
                ('modified_at', models.DateTimeField(auto_now=True, verbose_name='최근 수정 날짜')),
            ],
            options={
                'verbose_name_plural': '공지사항',
                'db_table': 'MUSE_Notice',
            },
        ),
    ]
