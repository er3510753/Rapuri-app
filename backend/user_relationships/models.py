# relationships/models.py
from django.db import models
from django.conf import settings

class UserRelationship(models.Model):
    """ユーザーのフォロー関係を管理するモデル"""
    class Status(models.TextChoices):
        PENDING = 'PENDING', '保留中'
        APPROVED = 'APPROVED', '承認済み'
        DENIED = 'DENIED', '拒否済み'

    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='following_relationships',
        on_delete=models.CASCADE,
        verbose_name='フォローしているユーザー'
    )
    followed = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='follower_relationships',
        on_delete=models.CASCADE,
        verbose_name='フォローされているユーザー'
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name='ステータス'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['follower', 'followed'], name='unique_follow')
        ]
        db_table = 'user_relationships'
        verbose_name = 'ユーザー関係'
        verbose_name_plural = 'ユーザー関係'
        ordering = ['-created_at']

    def __str__(self):
        status_display = self.get_status_display()
        return f"{self.follower.username} が {self.followed.username} をフォロー ({status_display})"

class IkitaiStatus(models.Model):
    """「ラーメンイキタイ」の状態を管理するモデル"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ikitai_status'
    )
    latitude = models.FloatField(help_text="ユーザーの現在地の緯度")
    longitude = models.FloatField(help_text="ユーザーの現在地の経度")
    expires_at = models.DateTimeField(help_text="このステータスが失効する日時")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - Ikitai until {self.expires_at.strftime('%Y-%m-%d %H:%M')}"
