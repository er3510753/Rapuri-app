from rest_framework import serializers
from .models import RamenLog
from django.contrib.auth import get_user_model

class RamenLogSerializer(serializers.ModelSerializer):
    # 修正点:
    # GETリクエスト（読み取り時）にはユーザー名を表示する
    user_name = serializers.CharField(source='user.username', read_only=True)
    # POSTリクエスト（書き込み時）にはユーザーIDを受け付ける
    # `queryset`で有効なユーザーが存在するかを検証してくれる
    user = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.all(), write_only=True
    )

    class Meta:
        model = RamenLog
        # user_nameを追加し、userは書き込み専用なので明示的に含める
        fields = ('id', 'shop_name', 'user', 'user_name', 'ordered_item', 'noodle_hardness', 'soup_richness', 'toppings', 'rating', 'visited_at')
