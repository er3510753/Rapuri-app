from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import UserSerializer, UserRegisterSerializer # 作成したシリアライザーをインポート
from rest_framework_simplejwt.tokens import RefreshToken # トークン発行のためにインポート
from .models import User

class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all() # Userモデル全体を対象とする
    serializer_class = UserRegisterSerializer # 使用するシリアライザーを指定
    permission_classes = [] # ユーザー登録時は認証不要

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # ユーザー作成と同時にトークンも作成
        refresh = RefreshToken.for_user(user)

        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "message": "ユーザー登録が完了しました。",
            # レスポンスにトークンを追加
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)