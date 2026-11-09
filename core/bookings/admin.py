from django.contrib import admin

from django.contrib import admin

from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("room", "guest", "date_in", "date_out", "status", "total_price")
    list_filter = ("status",)
    search_fields = ("room__name","owner",)
    readonly_fields = ("pay_per_night", "total_price", "created_date")
    
    fieldsets = (
        ('main info', {
            "fields": ("room", "guest", "status"),
        }),
        
        ('timeline', {
            "fields": ("date_in", "date_out"),             
        }),
        
        ('finance',{"fields":("pay_per_night","total_price", "created_date")})
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("room", "guest", "room__owner")