# ramen-app/backend/users/urls.py

from django.urls import path
from .views import UserRegisterView

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    # 他のユーザー関連APIもここに追加していく
]