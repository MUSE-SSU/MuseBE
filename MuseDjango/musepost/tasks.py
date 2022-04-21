import time
from celery import shared_task
from django.db.models import Count, F
from itertools import chain
import logging
from .models import Post, ColorOfWeek, PostColor

from colorthief import ColorThief
import webcolors
from .color_constants import COLOR_CHECK
from taggit.models import Tag
from config.settings import MUSE_SLACK_TOKEN, DEV
from common.slack_api import slack_post_message
from topics.models import Topic
from common.upload_file import origin_image_to_thumbnail_save


logger = logging.getLogger("api")

MUSE_SCORE = 100000


@shared_task
def thumbnail_extract():
    # 기존 이미지로 썸네일 만들어서 저장
    queryset = Post.objects.filter(idx__gte=374)
    # queryset = Post.objects.all()
    for obj in queryset:
        print(obj.idx)
        origin_image_to_thumbnail_save(obj)
    print("======DONE======")


def closest_colour(requested_colour):
    min_colours = {}
    for key, name in webcolors.css3_hex_to_names.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - requested_colour[0]) ** 2
        gd = (g_c - requested_colour[1]) ** 2
        bd = (b_c - requested_colour[2]) ** 2
        min_colours[(rd + gd + bd)] = name
    return min_colours[min(min_colours.keys())]


def get_colour_name(requested_colour):
    try:
        closest_name = actual_name = webcolors.rgb_to_name(requested_colour)
    except ValueError:
        closest_name = closest_colour(requested_colour)
        actual_name = None
    return actual_name, closest_name


@shared_task
def get_image_color():
    """이미지 색상 추출"""
    try:
        start_time = time.time()
        qs = Post.objects.filter(is_extract_color=False)

        if qs:
            for post in qs:
                color_thief = ColorThief(post.image)

                # get palette color - quality 1 is highest ~ lowest 10
                palette = color_thief.get_palette(color_count=5, quality=1)
                plt_name = []
                for plt in palette:
                    plt_actual_name, plt_closest_name = get_colour_name(plt)
                    if plt_actual_name:
                        plt_name.append(plt_actual_name)
                    else:
                        plt_name.append(plt_closest_name)

                # Replace Color Name with Spacing & Upper Case
                replace_colors = []
                for idx, full_color in enumerate(plt_name):
                    replace_color_name = full_color
                    for key, value in COLOR_CHECK.items():
                        if key in replace_color_name:
                            replace_color_name = replace_color_name.replace(
                                key, value + " "
                            )
                    replace_colors.append(replace_color_name.rstrip())

                # save color
                post_color = PostColor.objects.create(
                    post=post,
                    palette_color1=replace_colors[0],
                    palette_color2=replace_colors[1],
                    palette_color3=replace_colors[2],
                    palette_color4=replace_colors[3],
                    palette_color5=replace_colors[4],
                )

                post.is_extract_color = True
                post.save()

                if time.time() - start_time >= 1800:  # 30분이상
                    break

        slack_post_message(
            MUSE_SLACK_TOKEN,
            "#muse-dev" if DEV else "#muse-prod",
            f"🛠 게시물 이미지 색상 추출 완료",
        )
    except:
        slack_post_message(
            MUSE_SLACK_TOKEN,
            "#muse-dev-error" if DEV else "#muse-prod-error",
            "ERROR: 이미지 색상 추출",
        )


####################################################################
@shared_task
def select_weekly_tasks():
    """매주 일요일 자정 (뮤즈 선정 / 이번 주 색상 선정 / 모든 게시물 진행 상태 변경)"""
    try:
        select_muse()
        select_week_color()
        change_post_status()
        slack_post_message(
            MUSE_SLACK_TOKEN,
            "#muse-dev" if DEV else "#muse-prod",
            "🎉이번 주 뮤즈 선정 및 색상 선정 완료",
        )
    except:
        slack_post_message(
            MUSE_SLACK_TOKEN,
            "#muse-dev-error" if DEV else "#muse-prod-error",
            "ERROR: 이번 주 뮤즈 선정 및 색상 선정 에러 발생",
        )


def select_muse():
    """매주 일요일 00시: 뮤즈 선정"""
    # 좋아요 가장 많이 받은 게시물, 동점의 경우, 조회수 더 많은 게시물
    contest_post = Post.objects.filter(category="contest", cur_status=True)
    if contest_post:
        muse_post = contest_post.order_by("-likes", "-views").first()
        muse_post.is_muse = True
        muse_post.save()
        # 뮤즈 선정 점수
        muse_post.writer.profile.score += MUSE_SCORE
        muse_post.writer.profile.muse += 1
        muse_post.writer.profile.badge = 5
        muse_post.writer.profile.save()
    else:
        slack_post_message(
            MUSE_SLACK_TOKEN,
            "#muse-dev" if DEV else "#muse-prod",
            "🛠이번 주 콘테스트 게시물이 없습니다...!",
        )
    # 콘테스트 주제 week 변경
    past_topic = Topic.objects.get(activate_week=True)
    past_topic.activate_week = False
    current_week = past_topic.week + 1
    past_topic.save()
    Topic.objects.create(week=current_week)


def select_week_color():
    """매주 일요일 00시: 이번 주 가장 많이 사용된 색상 5가지"""
    try:
        # 지난 주 색상표 활성 상태 변경
        if ColorOfWeek.objects.all().count() >= 1:
            before_color_of_week = ColorOfWeek.objects.filter(cur_status=True)
            before_color_of_week.update(cur_status=False)

        week_post = PostColor.objects.filter(
            post__cur_status=True, post__is_extract_color=True
        )

        color1 = week_post.values(
            color=F("palette_color1"),
        ).annotate(count=Count("color"))
        color2 = week_post.values(
            color=F("palette_color2"),
        ).annotate(count=Count("color"))
        color3 = week_post.values(
            color=F("palette_color3"),
        ).annotate(count=Count("color"))
        color4 = week_post.values(
            color=F("palette_color4"),
        ).annotate(count=Count("color"))
        color5 = week_post.values(
            color=F("palette_color5"),
        ).annotate(count=Count("color"))

        color_list = color1.union(color2, color3, color4, color5, all=True)

        temp = {}
        for c in color_list:
            if c["color"] in temp:
                temp[c["color"]] += c["count"]
            else:
                temp[c["color"]] = c["count"]

        weekly_color = sorted(temp.items(), reverse=True, key=lambda item: item[1])[:5]

        cow = ColorOfWeek.objects.create(
            color1=weekly_color[0][0],
            color2=weekly_color[1][0],
            color3=weekly_color[2][0],
            color4=weekly_color[3][0],
            color5=weekly_color[4][0],
        )

        logger.info(f"INFO: CREATE WEEKLY COLOR > {cow}")
    except:
        logger.error("ERROR: WEEKLY COLOR")


def change_post_status():
    """이번 주의 전체 게시물(레퍼런스, 콘테스트) 현재 진행 상태 변경"""
    all_cur_post = Post.objects.filter(cur_status=True)
    all_cur_post.update(cur_status=False)


@shared_task
def remove_all_tags_without_objects():
    """어떤 게시물도 사용 안하는 해시태그 지우기"""
    try:
        for tag in Tag.objects.all():
            if tag.taggit_taggeditem_items.count() == 0:
                logger.info("Removing: {}".format(tag))
                tag.delete()
            else:
                logger.info("Keeping: {}".format(tag))
        slack_post_message(
            MUSE_SLACK_TOKEN,
            "#muse-dev" if DEV else "#muse-prod",
            "🛠 사용하지 않는 해시태그 삭제 완료",
        )
    except:
        logger.error("ERROR: REMOVE HASHTAG")
