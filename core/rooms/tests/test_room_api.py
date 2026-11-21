from django.urls import reverse
from rest_framework.test import APIClient
from datetime import datetime

from accounts.models import User
from ..models import Room

import pytest


@pytest.fixture
def api_client():
    client = APIClient()
    return client


@pytest.fixture
def common_test_user():
    user = User.objects.create_user(
        phone='09129129120',
        password='reza1385',
        is_verified=True
    )
    return user

@pytest.mark.django_db
class TestRoomApi:
    
    def test_get_room_response_200_status(self, api_client, common_test_user):
        user = common_test_user
        api_client.force_authenticate(user=user)
        url = reverse('rooms:api-v1:room-list')
        response = api_client.get(url)
        assert response.status_code == 200


# posting a room test

# getting details of a post test
        