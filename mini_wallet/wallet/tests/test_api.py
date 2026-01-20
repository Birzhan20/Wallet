import pytest
from django.urls import reverse
import threading
from concurrent.futures import ThreadPoolExecutor

from wallet.models import User, Wallet


@pytest.mark.django_db
def test_user_registration_creates_wallet(api_client):
    url = reverse('wallet:register')
    data = {
        "username": "new_tester",
        "email": "tester@example.com",
        "password": "strong_password123"
    }
    response = api_client.post(url, data=data, format='json')
    assert response.status_code == 201

    user = User.objects.get(username='new_tester')

    assert Wallet.objects.filter(user=user).exists()
    assert user.wallet.balance == 0


@pytest.mark.django_db
def test_money_transfer_success(api_client):
    sender = User.objects.create_user(username='sender_success', email='s_success@m.ru', password='123')
    receiver = User.objects.create_user(username='receiver_success', email='r_success@m.ru', password='123')

    sender.wallet.balance = 1000
    sender.wallet.save()

    api_client.force_authenticate(user=sender)
    url = reverse('wallet:transfer')
    data = {"receiver_email": "r_success@m.ru", "amount": 400}

    response = api_client.post(url, data=data, format='json')

    assert response.status_code == 200

    sender.wallet.refresh_from_db()
    receiver.wallet.refresh_from_db()

    assert sender.wallet.balance == 600
    assert receiver.wallet.balance == 400


@pytest.mark.django_db
def test_transfer_insufficient_funds(api_client):
    sender = User.objects.create_user(username='sender_insufficient', email='s_ins@m.ru', password='123')
    receiver = User.objects.create_user(username='receiver_insufficient', email='r_ins@m.ru', password='123')

    sender.wallet.balance = 100
    sender.wallet.save()

    api_client.force_authenticate(user=sender)
    url = reverse('wallet:transfer')

    response = api_client.post(url, {"receiver_email": "r_ins@m.ru", "amount": 500}, format='json')
    assert response.status_code == 400
    assert response.data['error'] == "Insufficient funds"

    sender.wallet.refresh_from_db()
    assert sender.wallet.balance == 100


@pytest.mark.django_db
def test_transfer_to_self_fails(api_client):
    sender = User.objects.create_user(username='sender_self', email='self@m.ru', password='123')

    sender.wallet.balance = 100
    sender.wallet.save()

    api_client.force_authenticate(user=sender)
    url = reverse('wallet:transfer')

    response = api_client.post(url, {"receiver_email": "self@m.ru", "amount": 100})

    assert response.status_code == 400


@pytest.mark.django_db(transaction=True)
def test_transfer_race_condition(api_client):
    from django.db import connections
    sender = User.objects.create_user(username='sender_race', email='race@m.ru', password='123')
    receiver = User.objects.create_user(username='receiver_race', email='receiv_race@m.ru', password='123')

    sender.wallet.balance = 100
    sender.wallet.save()

    url = reverse('wallet:transfer')
    data = {"receiver_email": "receiv_race@m.ru", "amount": 60}

    def make_request():
        try:
            api_client.force_authenticate(user=sender)
            return api_client.post(url, data, format='json')
        finally:
            connections.close_all()

    with ThreadPoolExecutor(max_workers=10) as executor:
        # Сразу превращаем в список, чтобы не потреблять генератор дважды!
        responses = list(executor.map(lambda _: make_request(), range(10)))

    status_codes = [r.status_code for r in responses]
    success_count = status_codes.count(200)
    failed_count = status_codes.count(400)

    sender.wallet.refresh_from_db()

    assert success_count == 1
    assert failed_count == 9
    assert sender.wallet.balance == 40
