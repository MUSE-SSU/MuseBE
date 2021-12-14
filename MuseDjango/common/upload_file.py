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
