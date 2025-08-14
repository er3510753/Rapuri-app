# ramen-app/backend/users/serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """ユーザー情報を表示するためのシリアライザ"""
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'created_at')


class UserRegisterSerializer(serializers.ModelSerializer):
    """ユーザー登録用のシリアライザ"""
    class Meta:
        model = User
        # 登録時に受け取るフィールドを指定
        fields = ('username', 'email', 'password')
        # パスワードは書き込み専用にし、APIのレスポンスには含めない
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        """
        バリデーション済みデータからユーザーを作成し、パスワードをハッシュ化する
        """
        user = User.objects.create_user(**validated_data)
        return user