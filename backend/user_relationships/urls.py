# relationships/urls.py
from django.urls import path
from .views import (
    FollowRequestView,
    FollowApprovalView,
    UnfollowView,
    FollowingListView,
    FollowerListView,
    PendingFollowRequestListView,
    IkitaiStatusView,
)

urlpatterns = [
    # フォローリクエストの送信 (POST /api/relationships/follow/)
    path('follow/', FollowRequestView.as_view(), name='follow-request'),

    # フォローリクエストの承認/拒否 (PATCH /api/relationships/approve/<int:user_id>/)
    # user_id は、フォローリクエストを送ってきたユーザーのID
    path('approve/<int:user_id>/', FollowApprovalView.as_view(), name='follow-approve'),

    # フォローの解除 (DELETE /api/relationships/unfollow/<int:user_id>/)
    # user_id は、アンフォローしたいユーザーのID
    path('unfollow/<int:user_id>/', UnfollowView.as_view(), name='unfollow'),

    # 自分がフォローしているユーザーの一覧 (GET /api/relationships/following/)
    path('following/', FollowingListView.as_view(), name='following-list'),

    # 自分をフォローしているユーザーの一覧 (GET /api/relationships/followers/)
    path('followers/', FollowerListView.as_view(), name='follower-list'),

    # 自分への保留中のフォローリクエストの一覧 (GET /api/relationships/pending-requests/)
    path('pending-requests/', PendingFollowRequestListView.as_view(), name='pending-follow-requests'),

    # 「ラーメンイキタイ」状態の取得(GET)/ON(POST)/OFF(DELETE)
    path('ikitai/', IkitaiStatusView.as_view(), name='ikitai-status'),
]