from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import NewRc, OldRc
from .serializers import NewRcSerializer, OldRcSerializer
from rest_framework.decorators import api_view


class NewRcCreateView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = NewRcSerializer(data=request.data)
        if serializer.is_valid():
            new_rc = (
                serializer.save()
            )  # This will call the save method of the NewRc model, generating the images
            return Response(
                NewRcSerializer(new_rc).data, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OldRcCreateView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = OldRcSerializer(data=request.data)
        if serializer.is_valid():
            old_rc = (
                serializer.save()
            )  # This will call the save method of the NewRc model, generating the images
            return Response(
                OldRcSerializer(old_rc).data, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def search_rc(request):
    reg_number = request.query_params.get("reg_number", None)
    if reg_number:
        # Query both models
        smart_rc_results = OldRc.objects.filter(reg_number__icontains=reg_number)
        new_rc_results = NewRc.objects.filter(reg_number__icontains=reg_number)

        # Serialize results
        smart_rc_serializer = OldRcSerializer(smart_rc_results, many=True)
        new_rc_serializer = NewRcSerializer(new_rc_results, many=True)

        # Combine results
        combined_results = smart_rc_serializer.data + new_rc_serializer.data

        return Response(combined_results)
    else:
        return Response({"error": "Please provide a reg_number to search."})
