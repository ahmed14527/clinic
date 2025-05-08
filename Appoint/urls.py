from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AppointmentSlotViewSet, BookingViewSet, AppointmentRequestViewSet

# Create a router and register the viewsets with it.
router = DefaultRouter()
router.register(r'appointment-slots', AppointmentSlotViewSet, basename='appointment-slot')
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'appointment-requests', AppointmentRequestViewSet, basename='appointment-request')

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('api/', include(router.urls)),  # Include the router-generated URLs
]
