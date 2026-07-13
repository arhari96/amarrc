from rest_framework.response import Response
from rest_framework.views import APIView

from .services import build_billing_summary


class BalanceListView(APIView):
    def get(self, request, *args, **kwargs):
        app_mode = request.query_params.get("app_mode", "new").lower()
        if app_mode not in ["new", "old"]:
            app_mode = "new"
        return Response(build_billing_summary(app=app_mode))
