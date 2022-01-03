from django.contrib import admin
from .models import *

from .color_constants import COLOR_CHECK
from colorthief import ColorThief
import webcolors


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


def admin_get_image_color(modeladmin, request, queryset):
    for post in queryset:
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


admin_get_image_color.short_description = "이미지 색상 추출"


class PostAdmin(admin.ModelAdmin):
    list_display = [
        "idx",
        "writer",
        "title",
        "image",
        "content",
        "views",
        "likes",
        "topic",
        "week",
        "hashtag",
        "ref_url",
        "dominant_color",
        "palette_color1",
        "palette_color2",
        "palette_color3",
        "category",
        "cur_status",
        "is_muse",
        "created_at",
        "modified_at",
    ]
    actions = [admin_get_image_color]
    list_per_page = 20


class PostLikeAdmin(admin.ModelAdmin):
    list_display = ["idx", "get_post_id", "get_like_user_id"]

    def get_post_id(self, obj):
        return obj.post.idx

    def get_like_user_id(self, obj):
        return obj.like_user.nickname

    get_post_id.short_description = "게시글"  # Renames column head
    get_like_user_id.short_description = "좋아요 누른 유저"  # Renames column head


class CommentAdmin(admin.ModelAdmin):
    list_display = [
        "idx",
        "get_post_id",
        "comment",
        "get_writer_id",
        "created_at",
        "modified_at",
    ]

    def get_post_id(self, obj):
        return obj.post.idx

    def get_writer_id(self, obj):
        return obj.writer.nickname

    get_post_id.short_description = "게시글"  # Renames column head
    get_writer_id.short_description = "댓글 작성자"  # Renames column head


class ColorOfWeekAdmin(admin.ModelAdmin):
    list_display = [
        "idx",
        "color1",
        "color2",
        "color3",
        "color4",
        "color5",
        "cur_status",
    ]


admin.site.register(Post, PostAdmin)
admin.site.register(PostLike, PostLikeAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(ColorOfWeek, ColorOfWeekAdmin)
