from django.urls import path
from .views import (
    RamenLogListCreateAPIView,
    RamenLogRetrieveAPIView,
    RamenLogDestroyAPIView,
)

urlpatterns = [
    path('ramenlog/', RamenLogListCreateAPIView.as_view(), name='ramenlog-list-create'),
    path('ramenlog/<int:pk>/', RamenLogRetrieveAPIView.as_view(), name='ramenlog-retrieve'),
    path('ramenlog/<int:pk>/delete/', RamenLogDestroyAPIView.as_view(), name='ramenlog-delete'),
]
