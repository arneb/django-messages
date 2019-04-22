from rest_framework.routers import DefaultRouter
from .viewset import MessageViewSet


router = DefaultRouter()
router.register(r'messages', MessageViewSet, basename='messages')
urlpatterns = router.urls
