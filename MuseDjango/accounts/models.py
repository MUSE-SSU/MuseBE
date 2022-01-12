from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils.text import slugify
from common.upload_file import upload_profile_image
from config.asset_storage import PublicMediaStorage
from common.upload_file import upload_post_image


class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, user_id, password, **extra_fields):

        if not user_id:
            raise ValueError("The given userid must be set")

        user_id = user_id
        user = self.model(user_id=user_id, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        user_pf = UserProfile.objects.create(user=user)
        user_pf.save()
        return user

    def create_user(self, user_id, password=None, **extra_fields):
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(user_id, password, **extra_fields)

    def create_superuser(self, user_id, password, **extra_fields):
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(user_id, password, **extra_fields)


class User(AbstractBaseUser):
    objects = CustomUserManager()
    idx = models.AutoField(primary_key=True, null=False, blank=False)

    user_id = models.CharField(max_length=100, verbose_name="아이디", unique=True)
    password = models.CharField(
        max_length=128, verbose_name="비밀번호", null=True, blank=True
    )
    username = models.CharField(max_length=100, verbose_name="이름")
    nickname = models.CharField(max_length=50, verbose_name="닉네임", unique=True)
    # slug = models.SlugField(unique=True, blank=True, null=True, allow_unicode=True,)

    date_joined = models.DateTimeField(verbose_name="최초 가입 날짜", auto_now_add=True)
    last_login = models.DateTimeField(verbose_name="최근 로그인 날짜", auto_now=True)

    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = "user_id"

    def __str__(self):
        return str(self.user_id)

    @property
    def is_staff(self):
        return self.is_superuser

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

    class Meta:
        db_table = "MUSE_User"
        verbose_name_plural = "유저"


class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        to_field="user_id",
        db_column="user_id",
        primary_key=True,
        related_name="profile",
        verbose_name="유저",
    )
    avatar = models.ImageField(
        upload_to=upload_profile_image,
        storage=PublicMediaStorage(),
        blank=True,
        null=True,
        verbose_name="프로필 사진",
    )
    self_introduce = models.CharField(
        max_length=300, blank=True, null=True, verbose_name="자기 소개"
    )
    instar_id = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="인스타ID"
    )
    score = models.PositiveIntegerField(default=0, verbose_name="유저 점수")
    badge = models.PositiveIntegerField(default=0, verbose_name="뱃지 단계")
    muse = models.PositiveIntegerField(default=0, verbose_name="뮤즈 선정 횟수")

    def __str__(self):
        return str(self.user)

    class Meta:
        db_table = "MUSE_UserProfile"
        verbose_name_plural = "유저 프로필"


class Follow(models.Model):
    following = models.ForeignKey(
        User,
        to_field="user_id",
        related_name="following",
        null=True,
        blank=True,
        verbose_name="팔로우 누른 사람",
        on_delete=models.CASCADE,
    )
    follower = models.ForeignKey(
        User,
        to_field="user_id",
        related_name="follower",
        null=True,
        blank=True,
        verbose_name="팔로우 눌린 사람",
        on_delete=models.CASCADE,
    )

    class Meta:
        db_table = "MUSE_UserFollow"
        verbose_name_plural = "팔로우"
