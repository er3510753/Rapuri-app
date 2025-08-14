from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # AbstractUserがDjangoに必要なフィールド（username, groups, user_permissionsなど）を
    # すべて提供しているため、ここではカスタムフィールドのみを定義します。
    # 必要に応じて、追加のフィールドをここに定義できます。
    created_at = models.DateTimeField(auto_now_add=True)