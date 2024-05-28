from django.db import models


# Create your models here.
class Balance(models.Model):
    recharge_amt = models.IntegerField(default=0)
    balance = models.IntegerField(default=0)
    debit_amount = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.balance} {self.date}"
