# relationships/views.py
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.utils import timezone

from .models import UserRelationship, IkitaiStatus
from .serializers import UserRelationshipSerializer, UserSerializer, FollowRequestSerializer, FollowApprovalSerializer, IkitaiStatusSerializer, IkitaiStatusCreateSerializer

User = get_user_model()

# --- フォロー機能 ---
class FollowRequestView(generics.CreateAPIView):
    """
    ユーザーをフォローするためのAPI。
    リクエストは保留中として作成される。
    """
    permission_classes = [IsAuthenticated]
    serializer_class = FollowRequestSerializer # リクエストボディを受け取るためのシリアライザ

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        followed_user_id = serializer.validated_data['user_id']

        try:
            followed_user = User.objects.get(id=followed_user_id)
        except User.DoesNotExist:
            return Response({'detail': 'フォロー対象のユーザーが見つかりません。'}, status=status.HTTP_404_NOT_FOUND)

        # 自分自身をフォローすることはできない
        if request.user == followed_user:
            return Response({'detail': '自分自身をフォローすることはできません。'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # フォロー関係を保留中として作成
            relationship = UserRelationship.objects.create(
                follower=request.user,
                followed=followed_user,
                status=UserRelationship.STATUS_PENDING # 初期ステータスは保留中
            )
            response_serializer = UserRelationshipSerializer(relationship)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except IntegrityError:
            # unique_together制約違反 (既にフォローリクエストがあるか、既にフォロー済み)
            existing_rel = UserRelationship.objects.filter(
                follower=request.user,
                followed=followed_user
            ).first()
            if existing_rel:
                if existing_rel.status == UserRelationship.STATUS_PENDING:
                    return Response({'detail': '既にフォローリクエストが保留中です。'}, status=status.HTTP_409_CONFLICT)
                elif existing_rel.status == UserRelationship.STATUS_APPROVED:
                    return Response({'detail': '既にフォローしています。'}, status=status.HTTP_409_CONFLICT)
            return Response({'detail': 'フォローリクエストの作成に失敗しました。'}, status=status.HTTP_400_BAD_REQUEST)


# --- フォロー承認機能 ---
class FollowApprovalView(generics.UpdateAPIView):
    """
    受信したフォローリクエストを承認または拒否するAPI。
    承認できるのはフォローされている側のユーザーのみ。
    """
    permission_classes = [IsAuthenticated]
    serializer_class = FollowApprovalSerializer
    http_method_names = ['patch'] # PATCHメソッドのみを許可

    def patch(self, request, *args, **kwargs):
        # URLからリクエスト元のユーザーID (フォローしているユーザーのID) を取得
        follower_user_id = self.kwargs.get('user_id')

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        action = serializer.validated_data['action'] # 'approve' or 'deny'

        try:
            # ログイン中のユーザーがフォローされているユーザーであるか確認
            # かつ、指定されたfollower_user_idからの保留中のリクエストを探す
            relationship = UserRelationship.objects.get(
                follower__id=follower_user_id,
                followed=request.user,
                status=UserRelationship.STATUS_PENDING # 保留中のリクエストのみを対象とする
            )
        except UserRelationship.DoesNotExist:
            return Response({'detail': '保留中のフォローリクエストが見つかりません。'}, status=status.HTTP_404_NOT_FOUND)

        if action == 'approve':
            relationship.status = UserRelationship.STATUS_APPROVED
            message = 'フォローリクエストを承認しました。'
            status_code = status.HTTP_200_OK
        elif action == 'deny':
            relationship.status = UserRelationship.STATUS_DENIED
            message = 'フォローリクエストを拒否しました。'
            status_code = status.HTTP_200_OK # 拒否も成功レスポンスとして200 OK
        else:
            return Response({'detail': '無効なアクションです。'}, status=status.HTTP_400_BAD_REQUEST)

        relationship.save()
        response_serializer = UserRelationshipSerializer(relationship)
        return Response({'detail': message, 'relationship': response_serializer.data}, status=status_code)


# --- フォロー削除機能 (アンフォロー) ---
class UnfollowView(generics.DestroyAPIView):
    """
    ユーザーのフォローを解除するAPI。
    ログイン中のユーザーがフォローしている関係のみ削除可能。
    """
    permission_classes = [IsAuthenticated]
    queryset = UserRelationship.objects.all()

    def delete(self, request, *args, **kwargs):
        followed_user_id = self.kwargs.get('user_id')

        if not followed_user_id:
            return Response({'detail': 'アンフォロー対象のuser_idがURLで指定されていません。'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            followed_user = User.objects.get(id=followed_user_id)
        except User.DoesNotExist:
            return Response({'detail': 'アンフォロー対象のユーザーが見つかりません。'}, status=status.HTTP_404_NOT_FOUND)

        try:
            # ログインしているユーザーが、指定されたユーザーをフォローしている関係を削除
            relationship = UserRelationship.objects.get(
                follower=request.user,
                followed=followed_user,
                status=UserRelationship.STATUS_APPROVED # 承認済みのフォローのみ削除対象
            )
            relationship.delete()
            return Response(status=status.HTTP_204_NO_CONTENT) # 成功時はコンテンツなし
        except UserRelationship.DoesNotExist:
            return Response({'detail': 'このユーザーをフォローしていません。または保留中のリクエストです。'}, status=status.HTTP_404_NOT_FOUND)


# --- 一覧表示機能 (自分がフォローしているユーザー一覧) ---
class FollowingListView(generics.ListAPIView):
    """
    ログイン中のユーザーがフォローしている（承認済み）ユーザーの一覧を表示するAPI。
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserRelationshipSerializer

    def get_queryset(self):
        # ログインしているユーザーがフォローしている、かつ承認済みの関係のみを返す
        return UserRelationship.objects.filter(
            follower=self.request.user,
            status=UserRelationship.STATUS_APPROVED
        ).select_related('followed') # followedユーザーの情報を効率的に取得


# --- 一覧表示機能 (自分をフォローしているユーザー一覧) ---
class FollowerListView(generics.ListAPIView):
    """
    ログイン中のユーザーをフォローしている（承認済み）ユーザーの一覧を表示するAPI。
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserRelationshipSerializer

    def get_queryset(self):
        # ログインしているユーザーをフォローしている、かつ承認済みの関係のみを返す
        return UserRelationship.objects.filter(
            followed=self.request.user,
            status=UserRelationship.STATUS_APPROVED
        ).select_related('follower') # followerユーザーの情報を効率的に取得


# --- フォローリクエスト一覧表示機能 ---
class PendingFollowRequestListView(generics.ListAPIView):
    """
    ログイン中のユーザーへの保留中のフォローリクエスト一覧を表示するAPI。
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserRelationshipSerializer

    def get_queryset(self):
        # ログインしているユーザーへの保留中のフォローリクエストを返す
        return UserRelationship.objects.filter(
            followed=self.request.user,
            status=UserRelationship.STATUS_PENDING
        ).select_related('follower')


# --- 「ラーメンイキタイ」機能 ---

class IkitaiStatusView(generics.GenericAPIView):
    """
    「ラーメンイキタイ」状態の取得(GET)、作成/更新(POST)、削除(DELETE)を行うAPI。
    エンドポイント: /api/relationships/ikitai/
    """
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return IkitaiStatusCreateSerializer
        return IkitaiStatusSerializer

    def get_object(self):
        try:
            # ログインユーザーのIkitaiStatusオブジェクトを取得
            return IkitaiStatus.objects.get(user=self.request.user)
        except IkitaiStatus.DoesNotExist:
            return None

    def get(self, request, *args, **kwargs):
        """自分の「ラーメンイキタイ」状態を取得する"""
        instance = self.get_object()
        if instance is None:
            return Response({'detail': '「ラーメンイキタイ」状態ではありません。'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        """「ラーメンイキタイ」状態をONにする (作成または更新)"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        now = timezone.now()
        duration_type = data['duration_type']

        if duration_type == 'now':
            expires_at = now + timezone.timedelta(hours=1)
        elif duration_type == 'lunch':
            expires_at = now.replace(hour=14, minute=0, second=0, microsecond=0)
            if now > expires_at: # 既に過ぎていたら明日にする
                expires_at += timezone.timedelta(days=1)
        elif duration_type == 'dinner':
            expires_at = now.replace(hour=22, minute=0, second=0, microsecond=0)
            if now > expires_at: # 既に過ぎていたら明日にする
                expires_at += timezone.timedelta(days=1)

        ikitai_status, created = IkitaiStatus.objects.update_or_create(
            user=request.user,
            defaults={'latitude': data['latitude'], 'longitude': data['longitude'], 'expires_at': expires_at}
        )

        response_serializer = IkitaiStatusSerializer(ikitai_status)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        """「ラーメンイキタイ」状態をOFFにする (削除)"""
        instance = self.get_object()
        if instance:
            instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)