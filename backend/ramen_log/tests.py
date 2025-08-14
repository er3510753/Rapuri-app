from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import RamenLog

User = get_user_model()

class RamenLogAPITests(APITestCase):
    def setUp(self):
        """テスト用のユーザーとクライアントをセットアップ"""
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)

        self.other_user = User.objects.create_user(username='otheruser', password='testpassword')
        RamenLog.objects.create(user=self.other_user, shop_name="他人のラーメン店")

    def test_create_ramen_log(self):
        """認証済みユーザーがラーメンログを作成できることをテスト"""
        url = reverse('ramenlog-list-create')
        data = {'shop_name': 'テスト軒', 'rating': 4.5}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(RamenLog.objects.count(), 2) # 他人のログと合わせて2件
        created_log = RamenLog.objects.get(shop_name='テスト軒')
        self.assertEqual(created_log.user, self.user)

    def test_list_ramen_logs_for_authenticated_user(self):
        """認証済みユーザーが自分のログのみを取得できることをテスト"""
        RamenLog.objects.create(user=self.user, shop_name="自分のラーメン店")

        url = reverse('ramenlog-list-create')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1) # 自分のログ1件のみ
        self.assertEqual(response.data[0]['shop_name'], '自分のラーメン店')
