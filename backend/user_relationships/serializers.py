# relationships/serializers.py
from rest_framework import serializers
from .models import UserRelationship, IkitaiStatus
from users.serializers import UserSerializer # usersアプリからUserSerializerをインポート

class UserRelationshipSerializer(serializers.ModelSerializer):
    # followerとfollowedの情報をネストして表示
    follower = UserSerializer(read_only=True)
    followed = UserSerializer(read_only=True)

    class Meta:
        model = UserRelationship
        fields = ['id', 'follower', 'followed', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'follower', 'status', 'created_at', 'updated_at']

class FollowRequestSerializer(serializers.Serializer):
    """フォローリクエスト用のシリアライザ (フォローするユーザーIDのみを受け取る)"""
    user_id = serializers.IntegerField(help_text="フォローしたいユーザーのID")

class FollowApprovalSerializer(serializers.Serializer):
    """フォロー承認/拒否用のシリアライザ"""
    action = serializers.ChoiceField(choices=[('approve', '承認'), ('deny', '拒否')], help_text="アクション: 'approve' または 'deny'")


# --- 「ラーメンイキタイ」機能のシリアライザ ---

class IkitaiStatusSerializer(serializers.ModelSerializer):
    """「ラーメンイキタイ」状態を表示するためのシリアライザ"""
    user = UserSerializer(read_only=True)

    class Meta:
        model = IkitaiStatus
        fields = ['id', 'user', 'latitude', 'longitude', 'expires_at', 'created_at']

class IkitaiStatusCreateSerializer(serializers.Serializer):
    """「ラーメンイキタイ」状態を作成するためのシリアライザ"""
    latitude = serializers.FloatField(write_only=True, min_value=-90.0, max_value=90.0)
    longitude = serializers.FloatField(write_only=True, min_value=-180.0, max_value=180.0)
    duration_type = serializers.ChoiceField(choices=['now', 'lunch', 'dinner'], write_only=True, help_text="期間タイプ: 'now'(1時間), 'lunch'(14時まで), 'dinner'(22時まで)")