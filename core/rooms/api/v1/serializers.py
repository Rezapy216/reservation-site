from rest_framework import serializers
from rest_framework.reverse import reverse
from ...models import Amenity, Room, Picture


class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = ["id", "name"]


class RoomSerializer(serializers.ModelSerializer):

    owner_name = serializers.CharField(source="owner.name", read_only=True)

    absolute_url = serializers.SerializerMethodField(method_name="get_abs_url")

    class Meta:
        model = Room
        fields = [
            "id",
            "owner_name",
            "name",
            "amenities",
            "permitted_guests",
            "pay_per_night",
            "absolute_url",
            "created_date",
            "is_active",
        ]

    def get_abs_url(self, obj):
        request = self.context.get("request")
        return reverse("rooms:room-detail", kwargs={"pk": obj.pk}, request=request)

    def to_representation(self, instance):
        request = self.context.get("request")
        data = super().to_representation(instance)
        data["amenities"] = AmenitySerializer(
            instance.amenities.all(), many=True, context=request
        ).data

        if request.parser_context.get("kwargs").get("pk"):
            data.pop("absolute_url", None)

        return data
