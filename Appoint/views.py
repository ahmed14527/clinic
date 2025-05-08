from rest_framework import viewsets, throttling, status
from rest_framework.response import Response
from .models import AppointmentSlot, Booking, AppointmentRequest
from .serializers import AppointmentSlotSerializer, BookingSerializer, AppointmentRequestSerializer
from rest_framework.permissions import IsAuthenticated

# Throttling
class StandardAnonThrottle(throttling.AnonRateThrottle):
    rate = '10/minute'

class StandardUserThrottle(throttling.UserRateThrottle):
    rate = '100/hour'

class ThrottleMixin:
    throttle_classes = [StandardAnonThrottle, StandardUserThrottle]


# ----- Appointment Slot ----- 
class AppointmentSlotViewSet(ThrottleMixin, viewsets.ModelViewSet):
    queryset = AppointmentSlot.objects.all()  # Directly setting the queryset
    serializer_class = AppointmentSlotSerializer  # Directly setting the serializer class
    permission_classes = [IsAuthenticated]  # Ensure that only authenticated users can access this view

    def get_queryset(self):
        user = self.request.user
        if user.role == 'doctor':
            return AppointmentSlot.objects.filter(doctor=user)  # Return only the slots assigned to the doctor
        return AppointmentSlot.objects.all()  # Otherwise, return all slots

    def perform_create(self, serializer):
        serializer.save(doctor=self.request.user)  # Assign the logged-in user (doctor) to the slot


# ----- Booking ----- 
class BookingViewSet(ThrottleMixin, viewsets.ModelViewSet):
    queryset = Booking.objects.all()  # Directly setting the queryset
    serializer_class = BookingSerializer  # Directly setting the serializer class
    permission_classes = [IsAuthenticated]  # Ensure that only authenticated users can access this view

    def get_queryset(self):
        user = self.request.user
        if user.role == 'patient':
            return Booking.objects.filter(patient=user)  # Return bookings for the logged-in patient
        elif user.role == 'doctor':
            return Booking.objects.filter(slot__doctor=user)  # Return bookings for the doctor
        return Booking.objects.none()  # Return no bookings for other roles

    def perform_create(self, serializer):
        slot = serializer.validated_data['slot']
        if slot.is_booked:
            return Response({'error': 'This slot is already booked.'}, status=status.HTTP_400_BAD_REQUEST)
        slot.is_booked = True
        slot.save()  # Mark the slot as booked
        serializer.save(patient=self.request.user)  # Save the booking with the logged-in patient


# ----- Appointment Request ----- 
class AppointmentRequestViewSet(ThrottleMixin, viewsets.ModelViewSet):
    queryset = AppointmentRequest.objects.all()  # Directly setting the queryset
    serializer_class = AppointmentRequestSerializer  # Directly setting the serializer class
    permission_classes = [IsAuthenticated]  # Ensure that only authenticated users can access this view

    def get_queryset(self):
        user = self.request.user
        if user.role == 'patient':
            return AppointmentRequest.objects.filter(patient=user)  # Return requests for the logged-in patient
        elif user.role in ['doctor', 'admin']:
            return AppointmentRequest.objects.all()  # Return all requests for doctors and admins
        return AppointmentRequest.objects.none()  # Return no requests for other roles

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)  # Save the appointment request with the logged-in patient
