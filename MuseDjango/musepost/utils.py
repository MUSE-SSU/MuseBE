import os
import uuid
from django.utils import timezone
from accounts.models import User
from topics.models import Topic


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

