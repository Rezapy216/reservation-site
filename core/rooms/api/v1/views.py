from rest_framework import status, viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import RoomSerializer
from .permissions import IsOwnerOrReadOnly
from .paginations import DefaultPagination
from ...models import Room


class RoomViewset(viewsets.ModelViewSet):
    queryset = Room.objects.select_related("owner").prefetch_related("amenities").all()
    serializer_class = RoomSerializer
    permission_classes = [IsOwnerOrReadOnly]
    pagination_class = DefaultPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["amenities", "owner", "permitted_guests"]
    search_fields = ["name", "owner__name", "permitted_guests"]
    ordering_fields = ["pay_per_night", "permitted_guests", "created_date"]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
