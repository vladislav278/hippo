from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Hospital
from .serializers import HospitalSerializer


class HospitalListView(generics.ListCreateAPIView):
    """API endpoint to list and create hospitals."""
    
    queryset = Hospital.objects.all()
    serializer_class = HospitalSerializer
    
    def get_permissions(self):
        """Allow anyone to list, but require auth to create."""
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

