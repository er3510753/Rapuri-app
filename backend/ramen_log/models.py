from django.db import models
from django.conf import settings

class RamenLog(models.Model):
    shop_name = models.CharField(max_length=100)
    # Userモデルへの関連付け (ForeignKey)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ramen_logs')
    ordered_item = models.CharField(max_length=100, blank=True, null=True)  # 空OK
    noodle_hardness = models.CharField(max_length=30, blank=True, null=True) # 空OK
    soup_richness = models.CharField(max_length=30, blank=True, null=True)   # スープの濃さ
    toppings = models.CharField(max_length=200, blank=True, null=True)       # 空OK
    rating = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)  # 空OK
    visited_at = models.DateTimeField(null=True, blank=True, default=None)
    def __str__(self):
        visited_date_str = self.visited_at.date() if self.visited_at else "訪問日未登録"
        return f"{self.shop_name} - {self.user.username} ({visited_date_str})"
