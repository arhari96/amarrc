from rest_framework import generics
from .models import Balance
from .serializers import BalanceSerializer
from rest_framework.response import Response


class BalanceListView(generics.ListAPIView):
    queryset = Balance.objects.all().order_by("-date")
    serializer_class = BalanceSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        # Calculate the total balance
        total_balance = sum([balance.balance for balance in queryset])

        # Add total balance to the response
        response = {"total_balance": total_balance, "balances": serializer.data}

        return Response(response)
