from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users.views import PaymentViewSet, UserViewSet

router = DefaultRouter()
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
]