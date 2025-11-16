from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Hospital
from .serializers import HospitalSerializer


class HospitalListCreateView(generics.ListCreateAPIView):
    """API endpoint for listing and creating hospitals."""
    
    queryset = Hospital.objects.all()
    serializer_class = HospitalSerializer
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]
