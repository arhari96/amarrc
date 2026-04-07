from rest_framework.response import Response
from rest_framework.views import APIView

from .services import build_billing_summary


class BalanceListView(APIView):
    def get(self, request, *args, **kwargs):
        return Response(build_billing_summary())
