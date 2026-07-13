from .models import Balance, BillingConfig, UsageTransaction
from .serializers import UsageTransactionSerializer


class BillingError(Exception):
    pass


def get_billing_config(lock_for_update=False, **kwargs):
    config = BillingConfig.get_solo()
    if lock_for_update:
        return BillingConfig.objects.select_for_update().get(pk=config.pk)
    return config


def build_billing_summary(app="new"):
    config = get_billing_config()
    transactions = UsageTransaction.objects.filter(app=app)[:50]
    latest_balance = Balance.objects.first()
    
    debit_amount = config.debit_amount if app == "new" else config.debit_amount_old

    return {
        "balance_amount": latest_balance.balance if latest_balance else 0,
        "usage": config.usage,
        "limit": config.limit,
        "debit_amount": debit_amount,
        "fetch_amount": config.fetch_amount,
        "edit_amount": config.edit_amount,
        "remaining_capacity": config.remaining_capacity,
        "projected_fetch_usage": config.usage + config.fetch_amount,
        "projected_create_usage": config.usage + debit_amount,
        "projected_edit_usage": config.usage + config.edit_amount,
        "can_fetch_rc": (config.usage + config.fetch_amount) <= config.limit,
        "can_create_rc": (config.usage + debit_amount) <= config.limit,
        "can_edit_rc": (config.usage + config.edit_amount) <= config.limit,
        "transactions": UsageTransactionSerializer(transactions, many=True).data,
    }


def apply_usage_charge(config, amount, transaction_type, reg_number=None, note="", app="new"):
    projected_usage = config.usage + amount
    if projected_usage > config.limit:
        raise BillingError("Usage limit reached. Please settle usage before continuing.")

    usage_before = config.usage
    usage_after = projected_usage
    config.usage = usage_after
    config.save(update_fields=["usage", "updated_at"])

    transaction = UsageTransaction(
        app=app,
        transaction_type=transaction_type,
        amount=amount,
        usage_before=usage_before,
        usage_after=usage_after,
        reg_number=reg_number,
        note=note,
    )
    transaction._skip_usage_apply = True
    transaction.save()
    return transaction
