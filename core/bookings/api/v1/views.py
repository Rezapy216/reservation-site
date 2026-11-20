from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import BookingSerializer
from .permissions import IsAdminOrReadOnly
from .paginations import DefaultPagination
from .filters import BookingFilter
from ...models import Booking


class BookingModelViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Booking.objects.select_related("room", "guest", "room__owner")
    serializer_class = BookingSerializer
    pagination_class = DefaultPagination
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = BookingFilter
