from celery import shared_task
from django.db.models import Count, F
import logging
from .models import Post, ColorOfWeek

from colorthief import ColorThief
import webcolors
from .color_constants import COLOR_CHECK
from taggit.models import Tag
from config.settings import MUSE_SLACK_TOKEN, DEV
from common.slack_api import slack_post_message
from topics.models import Topic

logger = logging.getLogger("api")

MUSE_SCORE = 100000


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
def get_image_color(post_idx):
    """이미지 색상 추출"""
    try:
        post = Post.objects.get(idx=post_idx)
    except:
        logger.error("ERROR: GET IMAGE COLOR > NONE OBJ")
    try:
        color_thief = ColorThief(post.image)

        # get domminat color
        dominant_color = color_thief.get_color(quality=1)
        dominant_actual_name, dominant_closest_name = get_colour_name(dominant_color)

        # get palette color
        palette = color_thief.get_palette(color_count=3)
        plt_name = []
        for plt in palette:
            plt_actual_name, plt_closest_name = get_colour_name(plt)
            if plt_actual_name:
                plt_name.append(plt_actual_name)
            else:
                plt_name.append(plt_closest_name)

        # Replace Color Name with Spacing & Upper Case
        temp_colors = []
        if dominant_actual_name:
            temp_colors.append(dominant_actual_name)
        else:
            temp_colors.append(dominant_closest_name)
        temp_colors.extend(plt_name)

        replace_colors = []
        for idx, full_color in enumerate(temp_colors):
            replace_color_name = full_color
            for key, value in COLOR_CHECK.items():
                if key in replace_color_name:
                    replace_color_name = replace_color_name.replace(key, value + " ")
            replace_colors.append(replace_color_name.rstrip())

        # save color
        post.dominant_color = replace_colors[0]
        post.palette_color1 = replace_colors[1]
        post.palette_color2 = replace_colors[2]
        post.palette_color3 = replace_colors[3]

        post.save()
    except:
        logger.error("=====ERROR: GET IMAGE COLOR=====")


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
    muse_post = contest_post.order_by("-likes", "-views").first()
    muse_post.is_muse = True
    muse_post.save()
    # 뮤즈 선정 점수
    muse_post.writer.profile.score += MUSE_SCORE
    muse_post.writer.profile.muse += 1
    muse_post.writer.profile.badge = 5
    muse_post.writer.profile.save()
    # 콘테스트 주제 week 변경
    past_topic = Topic.objects.filter(activate_week=True)
    past_topic.activate_week = False
    past_topic.save()
    current_week = past_topic.week + 1
    current = Topic.objects.create(week=current_week)


@shared_task
def select_week_color():
    """매주 일요일 00시: 이번 주 가장 많이 사용된 색상 5가지"""
    try:
        # # 지난 주 색상표 활성 상태 변경
        if ColorOfWeek.objects.all().count() >= 1:
            before_color_of_week = ColorOfWeek.objects.filter(cur_status=True)
            # before_color_of_week.cur_status = False
            # before_color_of_week.save()
            before_color_of_week.update(cur_status=False)

        week_post = Post.objects.filter(cur_status=True)
        week_dominant_color = (
            week_post.values("dominant_color")
            .annotate(count=Count("dominant_color"))
            .order_by("-count")
        )

        if week_dominant_color.count() >= 5:
            cow = ColorOfWeek.objects.create(
                color1=week_dominant_color[0]["dominant_color"],
                color2=week_dominant_color[1]["dominant_color"],
                color3=week_dominant_color[2]["dominant_color"],
                color4=week_dominant_color[3]["dominant_color"],
                color5=week_dominant_color[4]["dominant_color"],
            )
        else:
            additional_color = []
            for i, color in enumerate(week_dominant_color):
                additional_color.append(color["dominant_color"])

                week_palette_color1 = (
                    week_post.annotate(
                        palette_color=F("palette_color1"), count=Count("palette_color1")
                    )
                    .values("palette_color", "count")
                    .order_by("-count")
                )[:3]
                week_palette_color2 = (
                    week_post.annotate(
                        palette_color=F("palette_color2"), count=Count("palette_color2")
                    )
                    .values("palette_color", "count")
                    .order_by("-count")
                )[:3]
                week_palette_color3 = (
                    week_post.annotate(
                        palette_color=F("palette_color3"), count=Count("palette_color3")
                    )
                    .values("palette_color", "count")
                    .order_by("-count")
                )[:3]

                week_palette_color = (
                    list(week_palette_color1)
                    + list(week_palette_color2)
                    + list(week_palette_color3)
                )

                cnt = 5 - len(additional_color)
                i = 0
                while cnt > 0:
                    if week_palette_color[i]["palette_color"] not in additional_color:
                        additional_color.append(week_palette_color[i]["palette_color"])
                        cnt -= 1
                    i += 1

                cow = ColorOfWeek.objects.create(
                    color1=additional_color[0],
                    color2=additional_color[1],
                    color3=additional_color[2],
                    color4=additional_color[3],
                    color5=additional_color[4],
                )

        logger.info(f"INFO: CREATE WEEKLY COLOR > {cow}")
    except:
        logger.error("ERROR: WEEKLY COLOR")


def change_post_status():
    """매주 일요일 00시 30분: 이번 주의 전체 게시물(레퍼런스, 콘테스트) 현재 진행 상태 변경"""
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
