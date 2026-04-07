# Phase 01: Usage-Based Balance System

## Overview
Transform the current balance debit system to a usage-based model with transaction tracking and spending limits.

## Current System Problems
1. **Manual balance updates required** - Admin must manually add balance before RC creation
2. **No spending limits** - Users can overspend without controls
3. **No transaction history** - No audit trail for balance changes
4. **Confusing UX** - Balance shows remaining amount, not usage tracking

## Desired System Behavior

### Usage Model
- Each user/account has a **usage** field (starts at 0)
- Each user/account has a **limit** field (maximum allowed usage)
- When RC is created, usage increases by the debit_amount
- When usage reaches limit, no more RC creation allowed
- Admin can manually adjust limit

### Transaction Model
- New `Transaction` model tracks all balance additions
- When transaction is created (e.g., 50 units), it automatically reduces usage
- Formula: `effective_usage = usage - transaction_amount`
- Transactions provide audit trail for all balance changes

### Example Flow
```
Initial state: usage=0, limit=100
Create RC (cost 35): usage=35, limit=100
Create RC (cost 30): usage=65, limit=100
Add Transaction (50): usage=15, limit=100 (65-50=15)
Create RC (cost 20): usage=35, limit=100
Check before RC: if (usage + new_cost) > limit → block creation
```

## Requirements

### Backend Requirements
- [USAGE-01] Create Transaction model with amount, date, description fields
- [USAGE-02] Modify Balance model: rename `balance` to `usage`, add `limit` field
- [USAGE-03] Create signal/hook: Transaction creation auto-reduces usage
- [USAGE-04] Add validation: Block RC creation if (usage + cost) > limit
- [USAGE-05] Update balance API to show usage, limit, and transaction history
- [USAGE-06] Update RC creation endpoints to use new usage check logic
- [USAGE-07] Create migration for existing balance data conversion

### Admin Panel Requirements
- [ADMIN-01] Transaction inline admin for easy balance management
- [ADMIN-02] Balance admin shows current usage, limit, and transaction list
- [ADMIN-03] Admin action to adjust limit manually

### Frontend Requirements (Optional)
- [FRONT-01] Dashboard shows usage vs limit with progress bar
- [FRONT-02] Transaction history table with filters
- [FRONT-03] Warning when usage approaches limit (80% threshold)
- [FRONT-04] Improved RC creation form with cost preview
- [FRONT-05] Modern, attractive UI design updates

## Technical Approach

### Model Changes
```python
# New Transaction model
class Transaction(models.Model):
    balance = models.ForeignKey(Balance, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            # Auto-reduce usage when transaction created
            self.balance.usage = max(0, self.balance.usage - self.amount)
            self.balance.save()

# Modified Balance model
class Balance(models.Model):
    usage = models.IntegerField(default=0)  # renamed from balance
    limit = models.IntegerField(default=100)  # new field
    recharge_amt = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)
```

### RC Creation Validation
```python
def can_create_rc(cost):
    balance = Balance.objects.order_by("date").first()
    if not balance:
        return False, "No balance account found"
    
    effective_usage = balance.usage  # transactions already reduce usage
    if effective_usage + cost > balance.limit:
        return False, f"Usage limit exceeded. Current: {effective_usage}, Limit: {balance.limit}"
    
    balance.usage += cost
    balance.save()
    return True, "RC created successfully"
```

## Migration Strategy
1. Rename `balance` field to `usage` in database
2. Set default `limit` based on existing `recharge_amt` or reasonable default
3. Preserve existing `debit_amount` for reference
4. Create Transaction records from historical recharge data (if needed)

## Success Criteria
- [ ] Transaction model created with proper signals
- [ ] Balance model updated with usage/limit fields
- [ ] RC creation blocked when limit exceeded
- [ ] Transaction creation auto-reduces usage
- [ ] Admin panel allows easy transaction management
- [ ] API endpoints return usage/limit/transaction data
- [ ] Existing data migrated without loss
- [ ] (Optional) Frontend shows usage dashboard with modern design
