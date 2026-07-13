import json
import os

from django.conf import settings
from django.db import transaction as db_transaction
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from balance.models import UsageTransaction
from balance.services import apply_usage_charge, get_billing_config
from smartrc.models import Rc
from .models import NewRc, OldRc
from .serializers import NewRcSerializer, OldRcSerializer


def canonicalize_reg_number(value):
    return "".join(char for char in str(value or "").upper() if char.isalnum())


def to_plain_dict(data):
    if hasattr(data, "dict"):
        return data.dict()
    return dict(data)


def normalize_rc_type(rc_type):
    if not rc_type:
        return None
    normalized = rc_type.strip().lower()
    if normalized == "new":
        return "New"
    if normalized == "old":
        return "Old"
    return None


def get_rc_components(rc_type):
    normalized_type = normalize_rc_type(rc_type)
    if normalized_type == "New":
        return normalized_type, NewRc, NewRcSerializer
    if normalized_type == "Old":
        return normalized_type, OldRc, OldRcSerializer
    return None, None, None


def split_legacy_address(payload):
    address = payload.get("address") or payload.get("address_text") or ""
    if not address:
        return

    address_lines = address.split("\n")
    payload["street_name"] = address_lines[0] if len(address_lines) > 0 else ""
    payload["city"] = address_lines[1] if len(address_lines) > 1 else ""
    payload["district"] = address_lines[2] if len(address_lines) > 2 else ""
    payload["district1"] = address_lines[3] if len(address_lines) > 3 else ""
    payload.pop("address", None)
    payload.pop("address_text", None)


def prepare_old_rc_fields(payload):
    laden = payload.get("laden", "")
    unladen = payload.get("unladen", "")
    if laden and unladen:
        try:
            payload["ledan_unledan"] = f"{int(laden):06d}/{int(unladen):06d}"
        except (TypeError, ValueError):
            pass

    seating = payload.get("seating", "")
    if seating:
        if "/" in str(seating):
            payload["seating"] = seating
        else:
            try:
                payload["seating"] = f"{int(seating):03d}/00"
            except (TypeError, ValueError):
                pass

    month_year = payload.get("month_year_of_Mfg", "")
    if month_year and "/" in month_year:
        month, year = month_year.split("/")
        try:
            payload["month_year_of_Mfg"] = f"{int(month):02d}/{int(year):04d}"
        except (TypeError, ValueError):
            pass

    wheel_base = payload.get("wheel_base", "")
    if wheel_base and str(wheel_base).isdigit():
        payload["wheel_base"] = f"{int(wheel_base):06d}"

    cubic = payload.get("cubic", "")
    if cubic:
        if "." in str(cubic):
            whole, decimal = str(cubic).split(".", 1)
            try:
                payload["cubic"] = f"{int(whole):06d}.{decimal}"
            except (TypeError, ValueError):
                pass
        elif str(cubic).isdigit():
            payload["cubic"] = f"{int(cubic):06d}"

    num_cylinder = payload.get("number_cylinder", "")
    if num_cylinder and str(num_cylinder).isdigit():
        payload["number_cylinder"] = f"{int(num_cylinder):02d}"

    if payload.get("vehicle_class"):
        payload["type"] = payload["vehicle_class"]

    payload["owner_type"] = payload.get("owner_type") or "OWNER"
    payload["tax_valid"] = payload.get("tax_valid") or "LIFE TIME"


def filter_model_payload(model_class, payload):
    allowed_fields = {field.name for field in model_class._meta.fields}
    return {key: value for key, value in payload.items() if key in allowed_fields}


def prepare_rc_payload(raw_data, rc_type):
    normalized_type, model_class, _ = get_rc_components(rc_type)
    if not model_class:
        return None, None

    payload = to_plain_dict(raw_data)
    payload.pop("front_image", None)
    payload.pop("back_image", None)
    payload.pop("now", None)
    payload.pop("rc_type", None)

    split_legacy_address(payload)

    if normalized_type == "New":
        if not payload.get("horse_power"):
            payload["horse_power"] = "0"

    if normalized_type == "Old":
        prepare_old_rc_fields(payload)

    return normalized_type, filter_model_payload(model_class, payload)


def serialize_rc_record(instance, rc_type, serializer_class):
    return {"rc_type": rc_type, **serializer_class(instance).data}


def limit_error_message(action_label, amount, config):
    return (
        f"Usage limit reached. {action_label} needs {amount} usage, "
        f"but only {config.remaining_capacity} is available."
    )


def handle_rc_create(raw_data, explicit_rc_type=None):
    requested_type = explicit_rc_type or raw_data.get("rc_type")
    normalized_type, payload = prepare_rc_payload(raw_data, requested_type)
    _, _, serializer_class = get_rc_components(normalized_type)

    if not serializer_class:
        return Response(
            {"error": "Invalid 'rc_type' specified."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer = serializer_class(data=payload)
    if not serializer.is_valid():
        print("LEGACY SERIALIZER ERRORS:", serializer.errors, flush=True)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    reg_number = serializer.validated_data.get("reg_number")

    with db_transaction.atomic():
        config = get_billing_config(app="old", lock_for_update=True)
        amount = config.debit_amount_old
        if config.usage + amount > config.limit:
            return Response(
                {"error": limit_error_message("Creating this RC", amount, config)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        rc_instance = serializer.save()

        # Central cache: save to Rc JSON model
        prefill_data = build_prefill_from_saved_rc(rc_instance, normalized_type)
        Rc.objects.update_or_create(
            reg_number=reg_number,
            defaults={"data": prefill_data},
        )

        apply_usage_charge(
            config,
            amount,
            UsageTransaction.RC_CREATE,
            reg_number=reg_number,
            note=f"{normalized_type} RC created (Legacy)",
            app="old",
        )

    return Response(
        {
            "message": "Created Successfully",
            "rc_type": normalized_type,
            "reg_number": reg_number,
            "data": serializer_class(rc_instance).data,
        },
        status=status.HTTP_201_CREATED,
    )


def get_rc_instance(rc_type, reg_number):
    normalized_type, model_class, serializer_class = get_rc_components(rc_type)
    if not model_class:
        return None, None, None, Response(
            {"error": "Invalid 'rc_type' specified."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        instance = model_class.objects.get(reg_number=reg_number)
    except model_class.DoesNotExist:
        return normalized_type, model_class, serializer_class, Response(
            {"error": "RC not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    return normalized_type, model_class, serializer_class, instance


def build_prefill_from_saved_rc(instance, rc_type):
    if rc_type == "New":
        address_parts = [instance.street_name, instance.city, instance.district, instance.district1]
        return {
            "license_plate": instance.reg_number,
            "chassis_number": instance.chassis_number,
            "engine_number": instance.engine_number,
            "owner_name": instance.name,
            "father_name": instance.son_of,
            "permanent_address": ", ".join([part for part in address_parts if part]),
            "registration_date": instance.reg_date,
            "fuel_type": instance.fuel,
            "owner_count": instance.serial,
            "norms": instance.emission_norms,
            "cylinders": instance.number_cylinder,
            "class": instance.vehicle_class,
            "brand_name": instance.maker_name,
            "brand_model": instance.model_name,
            "color": instance.color,
            "seating_capacity": instance.seating,
            "cubic_capacity": instance.cubic,
            "is_financed": "1" if instance.financer else "0",
            "financer": instance.financer or "",
            "template": getattr(instance, "template", "NT_TN"),
        }

    seating_capacity = str(instance.seating or "").split("/")[0]
    laden_unladen = str(instance.ledan_unledan or "").split("/")
    return {
        "license_plate": instance.reg_number,
        "chassis_number": instance.chassis_number,
        "engine_number": instance.engine_number,
        "owner_name": instance.name,
        "father_name": instance.son_of,
        "permanent_address": ", ".join(
            [part for part in [instance.street_name, instance.city, instance.district, instance.district1] if part]
        ),
        "registration_date": instance.reg_date,
        "fuel_type": instance.fuel or "",
        "owner_count": instance.serial,
        "norms": "",
        "cylinders": instance.number_cylinder,
        "class": instance.type,
        "brand_name": instance.maker_name,
        "brand_model": instance.model_name,
        "color": instance.color,
        "seating_capacity": seating_capacity,
        "cubic_capacity": instance.cubic,
        "is_financed": "1" if instance.financer else "0",
        "financer": instance.financer or "",
        "body_type": instance.body_type,
        "unladden_weight": laden_unladen[1] if len(laden_unladen) > 1 else "",
        "gross_vehicle_weight": laden_unladen[0] if laden_unladen else "",
        "template": getattr(instance, "template", "NT_TN"),
    }


@api_view(["POST"])
def fetch_reg_detail(request):
    reg_number = request.data.get("reg_number")
    canonical_reg_number = canonicalize_reg_number(reg_number)

    if not canonical_reg_number:
        return Response(
            {"error": "Registration number is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    payload = None
    rc_data = Rc.objects.filter(reg_number__iexact=canonical_reg_number).first()
    if rc_data:
        payload = rc_data.data

    if payload is None:
        new_rc = NewRc.objects.filter(reg_number__iexact=canonical_reg_number).first()
        if new_rc:
            payload = build_prefill_from_saved_rc(new_rc, "New")

    if payload is None:
        old_rc = OldRc.objects.filter(reg_number__iexact=canonical_reg_number).first()
        if old_rc:
            payload = build_prefill_from_saved_rc(old_rc, "Old")

    if payload is None:
        return Response(
            {"error": "RC details not found for the provided registration number."},
            status=status.HTTP_404_NOT_FOUND,
        )

    with db_transaction.atomic():
        config = get_billing_config(app="old", lock_for_update=True)
        amount = config.fetch_amount
        if config.usage + amount > config.limit:
            return Response(
                {"error": limit_error_message("Fetching RC details", amount, config)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        apply_usage_charge(
            config,
            amount,
            UsageTransaction.RC_FETCH,
            reg_number=canonical_reg_number,
            note="RC details fetched (Legacy)",
            app="old",
        )

    return Response(payload, status=status.HTTP_200_OK)


class RCDetailCreateView(APIView):
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        return handle_rc_create(request.data)


class NewRcCreateView(APIView):
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        return handle_rc_create(request.data, explicit_rc_type="New")


class OldRcCreateView(APIView):
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        return handle_rc_create(request.data, explicit_rc_type="Old")


class RCDetailView(APIView):
    def get(self, request, rc_type, reg_number, *args, **kwargs):
        normalized_type, _, serializer_class, result = get_rc_instance(rc_type, reg_number)
        if isinstance(result, Response):
            return result
        return Response(
            serialize_rc_record(result, normalized_type, serializer_class),
            status=status.HTTP_200_OK,
        )

    def put(self, request, rc_type, reg_number, *args, **kwargs):
        normalized_type, _, serializer_class, result = get_rc_instance(rc_type, reg_number)
        if isinstance(result, Response):
            return result

        incoming_reg_number = request.data.get("reg_number")
        if incoming_reg_number and incoming_reg_number != reg_number:
            return Response(
                {"error": "reg_number cannot be changed during edit."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        body_type = request.data.get("rc_type")
        if body_type and normalize_rc_type(body_type) != normalized_type:
            return Response(
                {"error": "The rc_type in the request does not match the URL."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        _, payload = prepare_rc_payload(request.data, normalized_type)
        payload["reg_number"] = reg_number

        serializer = serializer_class(result, data=payload)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        with db_transaction.atomic():
            config = get_billing_config(app="old", lock_for_update=True)
            amount = config.edit_amount
            if config.usage + amount > config.limit:
                return Response(
                    {"error": limit_error_message("Editing this RC", amount, config)},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            rc_instance = serializer.save()

            # Central cache: save to Rc JSON model
            prefill_data = build_prefill_from_saved_rc(rc_instance, normalized_type)
            Rc.objects.update_or_create(
                reg_number=reg_number,
                defaults={"data": prefill_data},
            )

            apply_usage_charge(
                config,
                amount,
                UsageTransaction.RC_EDIT,
                reg_number=reg_number,
                note=f"{normalized_type} RC edited (Legacy)",
                app="old",
            )

        return Response(
            {
                "message": "Updated Successfully",
                "rc_type": normalized_type,
                "reg_number": reg_number,
                "data": serializer_class(rc_instance).data,
            },
            status=status.HTTP_200_OK,
        )


@api_view(["GET"])
def search_rc(request):
    reg_number = request.query_params.get("reg_number")
    if not reg_number:
        return Response(
            {"error": "Please provide a reg_number to search."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    old_results = OldRc.objects.filter(reg_number__icontains=reg_number)
    new_results = NewRc.objects.filter(reg_number__icontains=reg_number)

    old_data = [
        {"rc_type": "Old", **data}
        for data in OldRcSerializer(old_results, many=True).data
    ]
    new_data = [
        {"rc_type": "New", **data}
        for data in NewRcSerializer(new_results, many=True).data
    ]

    return Response(old_data + new_data, status=status.HTTP_200_OK)


@api_view(["DELETE"])
def delete_rc(request):
    reg_number = request.query_params.get("reg_number")
    if not reg_number:
        return Response(
            {"error": "Please provide a reg_number to delete."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    old_rc_deleted, _ = OldRc.objects.filter(reg_number=reg_number).delete()
    new_rc_deleted, _ = NewRc.objects.filter(reg_number=reg_number).delete()

    if old_rc_deleted == 0 and new_rc_deleted == 0:
        return Response(
            {"error": "No RC found with the provided reg_number."},
            status=status.HTTP_404_NOT_FOUND,
        )

    return Response(
        {"message": "RC(s) deleted successfully."},
        status=status.HTTP_200_OK,
    )
