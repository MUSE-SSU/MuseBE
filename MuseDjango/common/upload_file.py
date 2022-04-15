from django.utils import timezone
import os
import uuid


def upload_profile_image(instance, filename):
    prefix = timezone.now().strftime("%Y/%m/%d")
    file_name = uuid.uuid4().hex
    user_id = str(instance)
    avatar = "avatar"
    extension = os.path.splitext(filename)[-1].lower()  # 확장자 추출
    return "/".join(
        [
            prefix,
            user_id,
            avatar,
            file_name,
            extension,
        ]
    )


def upload_post_image(instance, filename):
    prefix = timezone.now().strftime("%Y/%m/%d")
    file_name = uuid.uuid4().hex
    user_id = str(instance.writer.user_id)
    post = "post"
    extension = os.path.splitext(filename)[-1].lower()  # 확장자 추출
    return "/".join(
        [
            prefix,
            user_id,
            post,
            file_name,
            extension,
        ]
    )


def upload_thumbnail_image(instance, filename):
    prefix = timezone.now().strftime("%Y/%m/%d")
    file_name = uuid.uuid4().hex
    user_id = str(instance.writer.user_id)
    post = "thumbnail"
    extension = os.path.splitext(filename)[-1].lower()  # 확장자 추출
    return "/".join(
        [
            prefix,
            user_id,
            post,
            file_name,
            extension,
        ]
    )


from django.core.files import File
from pathlib import Path
from PIL import Image
from io import BytesIO

image_types = {
    "jpg": "JPEG",
    "jpeg": "JPEG",
    "png": "PNG",
    "gif": "GIF",
    "tif": "TIFF",
    "tiff": "TIFF",
}


def image_resize(image, width=500, height=500):
    # Open the image using Pillow
    img = Image.open(image)

    # check if either the width or height is greater than the max
    if img.width > width or img.height > height:
        output_size = (width, height)
        # Create a new resized “thumbnail” version of the image with Pillow
        img.thumbnail(output_size)
        # Find the file name of the image
        img_filename = Path(image.file.name).name
        # Spilt the filename on “.” to get the file extension only
        img_suffix = Path(image.file.name).name.split(".")[-1]
        # Use the file extension to determine the file type from the image_types dictionary
        img_format = image_types[img_suffix]
        # Save the resized image into the buffer, noting the correct file type
        buffer = BytesIO()
        img.save(buffer, format=img_format)
        # return buffer.getvalue()
        # # Wrap the buffer in File object
        file_object = File(buffer)
        # # Save the new resized file as usual, which will save to S3 using django-storages
        image.save(img_filename, file_object)


def image_resize2(obj):
    # Open the image using Pillow
    img = Image.open(obj.image)
    width = int(img.width * 0.5)
    height = int(img.height * 0.5)
    # check if either the width or height is greater than the max
    if img.width > width or img.height > height:
        output_size = (width, height)
        # Create a new resized “thumbnail” version of the image with Pillow
        img.thumbnail(output_size)
        # Find the file name of the image
        img_filename = "tmp" + Path(obj.image.file.name).name
        # Spilt the filename on “.” to get the file extension only
        img_suffix = Path(obj.image.file.name).name.split(".")[-1]
        # Use the file extension to determine the file type from the image_types dictionary
        img_format = image_types[img_suffix]
        # Save the resized image into the buffer, noting the correct file type
        buffer = BytesIO()
        img.save(buffer, format=img_format)
        # Wrap the buffer in File object
        file_object = File(buffer)

        # Save the new resized file as usual, which will save to S3 using django-storages
        obj.thumbnail.save(img_filename, file_object)
    else:
        # Find the file name of the image
        img_filename = "tmp" + Path(obj.image.file.name).name
        # Spilt the filename on “.” to get the file extension only
        img_suffix = Path(obj.image.file.name).name.split(".")[-1]
        # Use the file extension to determine the file type from the image_types dictionary
        img_format = image_types[img_suffix]
        # Save the resized image into the buffer, noting the correct file type
        buffer = BytesIO()
        img.save(buffer, format=img_format)
        # Wrap the buffer in File object
        file_object = File(buffer)

        # Save the new resized file as usual, which will save to S3 using django-storages
        obj.thumbnail.save(img_filename, file_object)
