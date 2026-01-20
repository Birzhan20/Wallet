from django.db import transaction
from rest_framework import generics, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import Wallet, User, Transaction
from .serializers import UserSerializer, WalletSerializer, TransferSerializer


class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny,]


class WalletViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated,]

    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user)


class TransferAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = TransferSerializer(data=request.data)
        if serializer.is_valid():
            amount = serializer.validated_data['amount']
            with transaction.atomic():
                try:
                    sender_wallet = Wallet.objects.select_for_update().get(user=request.user)
                    receiver_email = serializer.validated_data['receiver_email']
                    receiver_user = User.objects.get(email=receiver_email)
                    receiver_wallet = receiver_user.wallet
                    if sender_wallet.balance < amount:
                        return Response({"error": "Insufficient funds"}, status=400)
                    if sender_wallet.user == receiver_wallet.user:
                        return Response({"error": "You cannot transfer money"}, status=400)
                    sender_wallet.balance -= amount
                    sender_wallet.save()
                    receiver_wallet.balance += amount
                    receiver_wallet.save()
                    Transaction.objects.create(
                        sender=sender_wallet,
                        receiver=receiver_wallet,
                        amount=amount,
                        status='SUCCESS'
                    )
                    return Response({"status": "Success"})
                except User.DoesNotExist:
                    return Response({"error": "Receiver not found"}, status=404)
        return Response(serializer.errors, status=400)