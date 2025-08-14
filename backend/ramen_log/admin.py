from django.contrib import admin
from .models import RamenLog

@admin.register(RamenLog)
class RamenLogAdmin(admin.ModelAdmin):
    """
    RamenLogモデルの管理画面表示をカスタマイズします。
    """
    list_display = ('shop_name', 'user', 'visited_at', 'rating')
    list_filter = ('user', 'visited_at', 'rating')
    search_fields = ('shop_name', 'user__username', 'ordered_item')
