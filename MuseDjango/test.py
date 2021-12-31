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


def get_image_color(image_url):
    color_thief = ColorThief(image_url)
    # get the dominant color
    dominant_color = color_thief.get_color(quality=1)
    # build a color palette
    palette = color_thief.get_palette(color_count=3)
    print(dominant_color)
    print(palette)
    actual_name, closest_name = get_colour_name(dominant_color)
    print(actual_name, closest_name)
    for plt in palette:
        actual_name, closest_name = get_colour_name(plt)
        print(actual_name, closest_name)


get_image_color(
    "https://muse-bucket.s3.ap-northeast-2.amazonaws.com/media/public/2021/12/31/1847747999/post/c3a1a3a39588422e810a961472d64ccc/.jpeg"
)
