from . import views
from rest_framework.routers import DefaultRouter

app_name = 'api-v1'

router = DefaultRouter()
router.register("room", views.RoomViewset, basename="room")
urlpatterns = router.urls
