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
from django.views.decorators.csrf import csrf_exempt

class TestView(APIView):

    def post(self, request):
        print(request.data)
        return Response({"message": "Hello, World!"})
    
@api_view(['POST'])
def fetch_reg_detail(request):
    # Extract the registration number from the request
    reg_number = request.data.get('reg_number')
    
    if not reg_number:
        return Response(
            {"error": "Registration number is required."}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    print(reg_number)
    # Simulated API response
    data_from_api= [{"action":"verify_with_source","completed_at":"2025-01-02T16:48:09+05:30","created_at":"2025-01-02T16:48:07+05:30","group_id":"8e16424a-58fc-4ba4-ab20-5bc8e7c3c41e","request_id":"5c1fd25e-f879-40df-88c8-c419dcc5eeab","result":{"extraction_output":{"noc_valid_upto":None,"seating_capacity":"2","fitness_upto":"2038-08-17","variant":None,"registration_number":"TN22DZ8174","npermit_upto":None,"manufacturer_model":"PULSAR NS 160","standing_capacity":"0","status":"id_found","is_financed":True,"status_message":None,"number_of_cylinder":"1","colour":"PEARL METALLIC WHITE","puc_valid_upto":"2024-08-17","vehicle_class":"2WN","permanent_address":"N NO 11 ESWARAN KOIL STREET, VENGADESHWARA APTS 2ND FLOOR, B BLOCK NO 19 ALANDUR, Chennai-600016","permit_no":"","father_name":"RAMAKRISHNAN A G","status_verfy_date":"2023-12-06","m_y_manufacturing":"2023-07","registration_date":"2023-08-18","gross_vehicle_weight":"303","registered_place":"MEENAMBAKKAM RTO, Tamil Nadu","permit_validity_upto":None,"insurance_policy_no":"MV819871","noc_details":"","npermit_issued_by":None,"sleeper_capacity":"0","current_address":"N NO 11 ESWARAN KOIL STREET, VENGADESHWARA APTS 2ND FLOOR, B BLOCK NO 19 ALANDUR, Chennai-600016","status_verification":"","permit_type":"","noc_status":None,"masked_name":False,"fuel_type":"PETROL","permit_validity_from":None,"owner_name":"HARI BABU A R","puc_number":"Newv4","owner_mobile_no":"","blacklist_status":"","manufacturer":"BAJAJ AUTO LTD","permit_issue_date":None,"engine_number":"JEXCPD91961","chassis_number":"MD2A92DXXPCD14211","mv_tax_upto":"2038-08-17","body_type":"SOLO WITH PILLION","unladden_weight":"153","insurance_name":"IFFCO TOKIO GENERAL INSURANCE CO. LTD.","owner_serial_number":"1","vehicle_category":"2WN","noc_issue_date":None,"npermit_no":"","cubic_capacity":"160.30","norms_type":"BHARAT STAGE VI","state":"Tamil Nadu","insurance_validity":"2028-08-15","financer":"BAJAJ AUTO FINANCE LTD","wheelbase":"1372"}},"status":"completed","task_id":"74f4c926-250c-43ca-9c53-453e87ceacd1","type":"ind_rc_plus"}]


    try:
        # Extract vehicle details from the simulated API response
        vehicle_detail = data_from_api[0]['result']['extraction_output']
        return Response(vehicle_detail, status=status.HTTP_200_OK)
    except (IndexError, KeyError) as e:
        return Response(
            {"error": "Unexpected error processing vehicle details."}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
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

    @csrf_exempt
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
