from django.core.exceptions import ValidationError
from django.db import models, transaction as db_transaction


class Balance(models.Model):
    recharge_amt = models.IntegerField(default=0)
    balance = models.IntegerField(default=0)
    debit_amount = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.balance} {self.date}"


class BillingConfig(models.Model):
    usage = models.IntegerField(default=0)
    limit = models.IntegerField(default=0)
    debit_amount = models.IntegerField(default=0)
    debit_amount_old = models.IntegerField(default=0)
    fetch_amount = models.IntegerField(default=0)
    edit_amount = models.IntegerField(default=0)
    limit_deduction_per_rc = models.IntegerField(
        default=0,
        help_text="Amount by which the limit decreases each time a brand-new RC is created.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Billing Config"
        verbose_name_plural = "Billing Config"

    def __str__(self):
        return f"Usage {self.usage}/{self.limit}"

    @property
    def remaining_capacity(self):
        return max(self.limit - self.usage, 0)

    def clean(self):
        existing = BillingConfig.objects.exclude(pk=self.pk)
        if existing.exists():
            raise ValidationError("Only one billing config record is allowed.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        instance = cls.objects.first()
        if instance is None:
            instance = cls.objects.create()
        return instance


class UsageTransaction(models.Model):
    RC_FETCH = "rc_fetch"
    RC_CREATE = "rc_create"
    RC_EDIT = "rc_edit"
    MANUAL_SETTLEMENT = "manual_settlement"

    TRANSACTION_TYPES = [
        (RC_FETCH, "RC Fetch"),
        (RC_CREATE, "RC Create"),
        (RC_EDIT, "RC Edit"),
        (MANUAL_SETTLEMENT, "Manual Settlement"),
    ]

    app = models.CharField(
        max_length=10,
        default="new",
        choices=[("new", "New App"), ("old", "Old App")],
    )
    transaction_type = models.CharField(max_length=32, choices=TRANSACTION_TYPES)
    amount = models.PositiveIntegerField()
    usage_before = models.IntegerField(default=0)
    usage_after = models.IntegerField(default=0)
    reg_number = models.CharField(max_length=10, blank=True, null=True)
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return f"{self.transaction_type} {self.amount}"

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        skip_usage_apply = getattr(self, "_skip_usage_apply", False)

        if (
            is_new
            and self.transaction_type == self.MANUAL_SETTLEMENT
            and not skip_usage_apply
        ):
            config = BillingConfig.get_solo()
            usage_before = config.usage
            usage_after = max(config.usage - self.amount, 0)
            self.usage_before = usage_before
            self.usage_after = usage_after

            with db_transaction.atomic():
                super().save(*args, **kwargs)
                config.usage = usage_after
                config.save(update_fields=["usage", "updated_at"])
            return

        super().save(*args, **kwargs)
