from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    نموذج مستخدم مخصص
    """
    email = models.EmailField(
        unique=True,
        verbose_name="البريد الإلكتروني"
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        verbose_name = "مستخدم"
        verbose_name_plural = "المستخدمون"

    def __str__(self):
        return self.email


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="المستخدم"
    )
    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        null=True,
        verbose_name="الصورة الشخصية"
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="رقم الجوال"
    )
    bio = models.TextField(
        blank=True,
        verbose_name="نبذة"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاريخ الإنشاء"
    )

    class Meta:
        verbose_name = "الملف الشخصي"
        verbose_name_plural = "الملفات الشخصية"

    def __str__(self):
        return f"الملف الشخصي - {self.user.email}"


class Address(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="addresses",
        verbose_name="المستخدم"
    )
    full_name = models.CharField(
        max_length=150,
        verbose_name="الاسم الكامل"
    )
    phone = models.CharField(
        max_length=20,
        verbose_name="رقم الجوال"
    )
    city = models.CharField(
        max_length=100,
        verbose_name="المدينة"
    )
    street = models.CharField(
        max_length=255,
        verbose_name="الشارع"
    )
    postal_code = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="الرمز البريدي"
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name="العنوان الافتراضي"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاريخ الإنشاء"
    )

    class Meta:
        verbose_name = "عنوان"
        verbose_name_plural = "العناوين"

    def __str__(self):
        return f"{self.city} - {self.user.email}"
