from django_filters import rest_framework as filters
from ...models import Booking


class BookingFilter(filters.FilterSet):
    min_total_price = filters.NumberFilter(field_name="total_price", lookup_expr="gte")
    max_total_price = filters.NumberFilter(field_name="total_price", lookup_expr="lte")
    max_pay_per_night_price = filters.NumberFilter(
        field_name="pay_per_night", lookup_expr="lte"
    )
    min_pay_per_night_price = filters.NumberFilter(
        field_name="pay_per_night", lookup_expr="gte"
    )

    class Meta:
        model = Booking
        fields = ["room", "guest"]
