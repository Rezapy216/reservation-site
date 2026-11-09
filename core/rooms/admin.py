from django.contrib import admin
from django.contrib.admin import ModelAdmin
from .models import Room, Amenity, Picture

class PictureInline(admin.TabularInline):
    model = Picture
    extra = 1


class AdminRoom(ModelAdmin):
    list_filter = ("permitted_guests",)
    list_display = ("name", "owner", "pay_per_night", "permitted_guests")
    filter_horizontal = ("amenities",)
    search_fields = ("owner__name", "owner__phone")
    inlines = [PictureInline]
    
    fieldsets = (
        ("Rooms",  {
            "classes": ("wide",),
            "fields": (
                "name", "owner", "amenities", "pay_per_night", "permitted_guests"
            )}),
    )


admin.site.register(Room, AdminRoom)
admin.site.register(Amenity)
admin.site.register(Picture)

