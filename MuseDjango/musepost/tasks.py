from celery import shared_task
from .models import Post
from colorthief import ColorThief
import webcolors
from celery import Celery
from .models import Post

app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")


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


@app.task
def get_image_color(post_idx):
    try:
        print("asdfadsf")
        post = Post.objects.get(post_idx)
        color_thief = ColorThief(
            "https://muse-bucket.s3.ap-northeast-2.amazonaws.com/media/public/2021/12/31/1847747999/post/c3a1a3a39588422e810a961472d64ccc/.jpeg"
        )

        # get domminat color
        dominant_color = color_thief.get_color(quality=1)
        dominant_actual_name, dominant_closest_name = get_colour_name(dominant_color)

        if dominant_actual_name:
            post.dominant_color = dominant_actual_name
        else:
            post.dominant_color = dominant_closest_name

        # get palette color
        palette = color_thief.get_palette(color_count=3)
        plt_name = []
        for plt in palette:
            plt_actual_name, plt_closest_name = get_colour_name(plt)
            if plt_actual_name:
                plt_name.append(plt_actual_name)
            else:
                plt_name.append(plt_closest_name)

        post.palette_color1 = plt_name[0]
        post.palette_color2 = plt_name[1]
        post.palette_color3 = plt_name[2]

    except:
        print("erroror")


@shared_task
def print_hello():
    print("print hello world!!!")


@shared_task
def select_muse():
    # 뮤즈 선정
    # 좋아요 가장 많이 받은 게시물, 동점의 경우, 조회수 더 많은 게시물
    contest_post = Post.objects.filter(is_contest=True, cur_status=True)
    muse_post = contest_post.order_by("-likes", "-views").first()
    muse_post.is_muse = True
    # 뮤즈 선정된 유저 뱃지 증가
    muse_post.writer.profile.badge += 1
    muse_post.save()

    # 게시물 현재 진행 상태 변경
    for i in contest_post:
        i.cur_status = False
        i.save()
