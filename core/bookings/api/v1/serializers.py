from rest_framework import serializers
from ...models import Booking


class BookingSerializer(serializers.ModelSerializer):

    owner = serializers.IntegerField(source="room.owner.id", read_only=True)
    owner_phone_number = serializers.CharField(
        source="room.owner.phone", read_only=True
    )
    guest_phone_number = serializers.CharField(source="guest.phone", read_only=True)

    class Meta:
        model = Booking
        fields = [
            "id",
            "owner",
            "owner_phone_number",
            "room",
            "guest",
            "guest_phone_number",
            "status",
            "number_of_people",
            "pay_per_night",
            "total_price",
            "date_in",
            "date_out",
        ]

        read_only_fields = ["room", "guest", "date_in", "date_out"]
