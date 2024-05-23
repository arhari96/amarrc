from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import FrontRcNew
from .serializers import FrontRcNewSerializer

# Create your views here.


@api_view(["POST"])
def create_frontrc(request):
    serializer = FrontRcNewSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
def delete_frontrc(request, reg_number):
    print(reg_number)
    try:
        front_rc = FrontRcNew.objects.get(reg_number=reg_number)
        front_rc.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except FrontRcNew.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
