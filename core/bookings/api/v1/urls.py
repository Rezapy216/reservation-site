from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register("booking", views.BookingModelViewSet, basename="booking")

urlpatterns = router.urls
