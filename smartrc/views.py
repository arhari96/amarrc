from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import NewRc, OldRc
from .serializers import NewRcSerializer, OldRcSerializer
from rest_framework.decorators import api_view
from balance.models import Balance
from django.views.generic import View
import os
from django.http import HttpResponse
from django.conf import settings


class ReactAppView(View):

    def get(self, request):
        try:

            with open(os.path.join(settings.REACT_APP_BUILD_DIR, "index.html")) as file:
                return HttpResponse(file.read())

        except:
            return HttpResponse(
                """
                index.html not found ! build your React app !!
                """,
                status=501,
            )


class NewRcCreateView(APIView):

    def post(self, request, *args, **kwargs):
        serializer = NewRcSerializer(data=request.data)
        if serializer.is_valid():
            # Fetch the balances ordered by date
            balance_entries = Balance.objects.order_by("date")

            if not balance_entries.exists():
                return Response(
                    {"error": "No balance available."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Get the first debit amount
            remaining_debit = balance_entries.first().debit_amount

            for entry in balance_entries:
                if remaining_debit <= 0:
                    break

                if entry.balance > 0:
                    if entry.balance >= remaining_debit:
                        entry.balance -= remaining_debit
                        entry.save()
                        remaining_debit = 0
                    else:
                        remaining_debit -= entry.balance
                        entry.balance = 0
                        entry.save()

            if remaining_debit > 0:
                # Handle case where not enough balance is available
                print("Not enough balance to cover the debit amount.")
                return Response(
                    {"error": "Not enough balance to cover the debit amount."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Save the RC only if the debit process is successful
            new_rc = (
                serializer.save()
            )  # This will call the save method of the NewRc model, generating the images
            return Response("Created Successfully", status=status.HTTP_201_CREATED)

        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OldRcCreateView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = OldRcSerializer(data=request.data)
        if serializer.is_valid():
            balance_entries = Balance.objects.order_by("date")

            if not balance_entries.exists():
                return Response(
                    {"error": "No balance available."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Get the first debit amount
            remaining_debit = balance_entries.first().debit_amount

            for entry in balance_entries:
                if remaining_debit <= 0:
                    break

                if entry.balance > 0:
                    if entry.balance >= remaining_debit:
                        entry.balance -= remaining_debit
                        if entry.balance == 0:
                            entry.delete()
                        else:
                            entry.save()
                        remaining_debit = 0
                    else:
                        remaining_debit -= entry.balance
                        entry.delete()

            if remaining_debit > 0:
                # Handle case where not enough balance is available
                return Response(
                    {"error": "Not enough balance to cover the debit amount."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
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

        # Add the additional parameter
        smart_rc_data = [
            {"rc_type": "Old", **data} for data in smart_rc_serializer.data
        ]
        new_rc_data = [{"rc_type": "New", **data} for data in new_rc_serializer.data]

        # Combine results
        combined_results = smart_rc_data + new_rc_data

        return Response(combined_results)
    else:
        return Response({"error": "Please provide a reg_number to search."})


@api_view(["DELETE"])
def delete_rc(request):
    reg_number = request.query_params.get("reg_number", None)
    if reg_number:
        # Try to delete from OldRc
        old_rc_deleted, old_rc_info = OldRc.objects.filter(
            reg_number=reg_number
        ).delete()

        # Try to delete from NewRc
        new_rc_deleted, new_rc_info = NewRc.objects.filter(
            reg_number=reg_number
        ).delete()

        # If no records were deleted
        if old_rc_deleted == 0 and new_rc_deleted == 0:
            return Response(
                {"error": "No RC found with the provided reg_number."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {"message": "RC(s) deleted successfully."}, status=status.HTTP_200_OK
        )
    else:
        return Response(
            {"error": "Please provide a reg_number to delete."},
            status=status.HTTP_400_BAD_REQUEST,
        )
