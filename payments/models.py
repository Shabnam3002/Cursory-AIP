from django.db import models
from django.conf import settings
from decimal import Decimal
from django.core.exceptions import ValidationError

class Wallet(models.Model):
    # 1 User = 1 Wallet configuration
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    balance_inr = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_withdrawn_inr = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    def can_withdraw(self):
        # Minimum threshold logic
        return self.balance_inr >= Decimal('500.00')

class Transaction(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
    ]
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    amount_inr = models.DecimalField(max_digits=12, decimal_places=2)
    upi_id = models.CharField(max_length=100, null=True, blank=True) 
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    def clean(self):
        # Backend validation to prevent negative balance or bypassing the limit
        if self.amount_inr is None:
            raise ValidationError("Please enter the withdrawal amount.")
        if self.wallet and self.amount_inr > self.wallet.balance_inr:
            raise ValidationError(f"Insufficient balance. Current balance: ₹{self.wallet.balance_inr}")

    def save(self, *args, **kwargs):
        self.full_clean() # Trigger validation checks
        
        is_new = self.pk is None
        if not is_new:
            old_status = Transaction.objects.get(pk=self.pk).status
            # Auto-deduct balance only when admin accepts the withdrawal
            if old_status == 'PENDING' and self.status == 'ACCEPTED':
                self.wallet.balance_inr -= self.amount_inr
                self.wallet.total_withdrawn_inr += self.amount_inr
                self.wallet.save()
        super().save(*args, **kwargs)

class EarningLog(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='earnings')
    views_count = models.PositiveIntegerField(default=0)
    rate_per_million_usd = models.DecimalField(max_digits=10, decimal_places=2)
    amount_inr = models.DecimalField(max_digits=12, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        # Dynamic Formula: (Views / 1,000,000) * Rate * Exchange_Rate
        exchange_rate = Decimal('83.00')
        self.amount_inr = (Decimal(self.views_count) / Decimal('1000000')) * self.rate_per_million_usd * exchange_rate
        
        super().save(*args, **kwargs)
        
        # Auto-credit calculated INR to user's wallet
        self.wallet.balance_inr += self.amount_inr
        self.wallet.save()
