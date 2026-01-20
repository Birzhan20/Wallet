from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserRegistrationView, WalletViewSet, TransferAPIView

app_name = 'wallet'

router = DefaultRouter()
router.register(r'wallets', WalletViewSet, basename='wallet')

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('transfer/', TransferAPIView.as_view(), name='transfer'),
    path('', include(router.urls)),
]
