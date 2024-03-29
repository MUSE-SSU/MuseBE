from django.contrib import admin
from .models import *

from .color_constants import COLOR_CHECK
from colorthief import ColorThief
import webcolors
from common.upload_file import origin_image_to_thumbnail_save


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
    try:
        for post in queryset:
            color_thief = ColorThief(post.image)

            # get domminat color
            dominant_color = color_thief.get_color(quality=1)
            dominant_actual_name, dominant_closest_name = get_colour_name(
                dominant_color
            )

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
                        replace_color_name = replace_color_name.replace(
                            key, value + " "
                        )
                replace_colors.append(replace_color_name.rstrip())

            # save color
            post.dominant_color = replace_colors[0]
            post.palette_color1 = replace_colors[1]
            post.palette_color2 = replace_colors[2]
            post.palette_color3 = replace_colors[3]

            post.save()
    except:
        print("ERROR: ADMIN GET IMAGE COLOR")


def admin_origin_image_to_thumbnail_save(modeladmin, request, queryset):
    try:
        for q in queryset:
            if not q.thumbnail:
                origin_image_to_thumbnail_save(q)
    except:
        print("ERROR: ADMIN ORIGIN IMAGEW TO THUMBNAIL")


admin_get_image_color.short_description = "이미지 색상 추출"
admin_origin_image_to_thumbnail_save.short_description = "이미지 썸네일 추출"


class PostAdmin(admin.ModelAdmin):
    list_display = [
        "idx",
        "get_writer",
        "title",
        "content",
        "views",
        "likes",
        "get_image",
        "get_thumbnail",
        "get_hashtag",
        "category",
        "ref_url",
        "topic",
        "week",
        "is_muse",
        "is_extract_color",
        "cur_status",
        "usage",
        "created_at",
        "modified_at",
    ]
    search_fields = ["title", "writer__nickname"]

    def get_writer(self, obj):
        return obj.writer.nickname

    def get_image(self, obj):
        return str(obj.image)[:22]

    def get_thumbnail(self, obj):
        return str(obj.thumbnail)[:22]

    def get_hashtag(self, obj):
        tags = []
        for tag in obj.hashtag.all():
            tags.append(str(tag))
        return ", ".join(tags)

    get_image.short_description = "이미지"
    get_thumbnail.short_description = "썸네일"
    get_hashtag.short_description = "해시태그"

    actions = [admin_get_image_color, admin_origin_image_to_thumbnail_save]
    list_per_page = 20


class PostColorAdmin(admin.ModelAdmin):
    list_display = [
        "idx",
        "get_post_id",
        "palette_color1",
        "palette_color2",
        "palette_color3",
        "palette_color4",
        "palette_color5",
    ]

    def get_post_id(self, obj):
        return obj.post.idx

    get_post_id.short_description = "게시글"  # Renames column head


class PostLikeAdmin(admin.ModelAdmin):
    list_display = ["idx", "get_post_id", "get_like_user_id"]

    def get_post_id(self, obj):
        return obj.post.idx

    def get_like_user_id(self, obj):
        return obj.like_user.nickname

    get_post_id.short_description = "게시글"  # Renames column head
    get_like_user_id.short_description = "좋아요 누른 유저"  # Renames column head


class PostBookmarkAdmin(admin.ModelAdmin):
    list_display = ["idx", "get_post_id", "get_user_id"]

    def get_post_id(self, obj):
        return obj.post.idx

    def get_user_id(self, obj):
        return obj.user.nickname

    get_post_id.short_description = "게시글"  # Renames column head
    get_user_id.short_description = "북마크 누른 유저"  # Renames column head


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

    get_post_id.short_description = "게시글"
    get_writer_id.short_description = "작성자"


class ColorOfWeekAdmin(admin.ModelAdmin):
    list_display = [
        "idx",
        "color1",
        "color2",
        "color3",
        "color4",
        "color5",
        "cur_status",
        "created_at",
    ]


admin.site.register(Post, PostAdmin)
admin.site.register(PostColor, PostColorAdmin)
admin.site.register(PostLike, PostLikeAdmin)
admin.site.register(PostBookmark, PostBookmarkAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(ColorOfWeek, ColorOfWeekAdmin)
