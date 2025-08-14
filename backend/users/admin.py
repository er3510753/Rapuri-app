from django.contrib import admin
from django.contrib.auth.admin import UserAdmin # UserAdminをインポート
from .models import User # あなたのカスタムUserモデルをインポート

@admin.register(User) # <-- このデコレータでUserモデルを管理画面に登録
class CustomUserAdmin(UserAdmin):
    # UserAdminを継承することで、デフォルトのユーザー管理画面の多くの機能を引き継ぎます
    # 必要に応じて、ここに管理画面での表示項目などをカスタマイズできます
    pass