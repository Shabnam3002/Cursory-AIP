from django.db import models, transaction
from django.conf import settings
from decimal import Decimal
from django.core.exceptions import ValidationError, ObjectDoesNotExist
#from dajngo.admin import SupportRequest
from django.core.exceptions import ObjectDoesNotExist as RelatedObjectDoesNotExist

# Create your models here.

class Wallet(models.Model):
    ## (1 User = 1 Wallet)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Balance INR (Decimal using for = bettr accuracy )
    balance_inr = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_withdrawn_inr = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    def __str__(self):
        return f"{self.user.username}'s Wallet - ₹{self.balance_inr}"

    
    def can_withdraw(self):
        return self.balance_inr >= Decimal('500.00')

class Transaction(models.Model):
    # Status options: verificaation workfor organize
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
    ]

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    amount_inr = models.DecimalField(max_digits=12, decimal_places=2)
    upi_id = models.CharField(max_length=100, null=True, blank=True) #optional
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at =models.DateTimeField(auto_now_add=True) #request date and time
    updated_at = models.DateTimeField(auto_now=True) # status change

    account_number = models.CharField(max_length=25, null=True, blank=True)
    ifsc_code = models.CharField( max_length = 15, null=True, blank=True)
    account_holder_name = models.CharField (max_length= 100, null=True, blank=True)

    def clean(self):
        if self.amount_inr is None:
            raise ValidationError("Please enter the withdrawal amount.")
        
        try:
            if self.wallet:
                if self.amount_inr < Decimal('500.00'):
                    raise ValidationError("The  minimum withdrawal amount is ₹500.")

                if self.amount_inr > self.wallet.balance_inr:
                    raise ValidationError(f"You do not have sufficient balance.  Current balance: ₹{self.wallet.balance_inr}")
        except RelatedObjectDoesNotExist:
            pass

    def save(self, *args, **kwargs):
        self.full_clean() #validation check. that'll call the clean() method aboce before saving
        # transaction already save? check it
        is_new = self.pk is None #'new or old'

        if is_new:
            if self.status == 'ACCEPTED':
                self.wallet.balance_inr -= self.amount_inr
                self.wallet.total_withdrawn_inr += self.amount_inr
                self.wallet.save()

        else:
            old_status = Transaction.objects.get(pk=self.pk).status
          #balance will cut when, shows status only "pending to accepted"
            if old_status == 'PENDING'and self.status == 'ACCEPTED':
             #cut the balance & increase withdrawn amount h  
                self.wallet.balance_inr -= self.amount_inr
                self.wallet.total_withdrawn_inr += self.amount_inr
                self.wallet.save()

            elif old_status == 'ACCEPTED' and self.status == 'REJECTED':
                self.wallet.balance_inr += self.amount_inr
                self.wallet.total_withdrawn_inr -= self.amount_inr
                self.wallet.save()    

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.wallet.user.username} - ₹{self.amount_inr} ({self.status})"        

class SupportRequest(models.Model): #contact-Us 
    CATEGORY_CHOICES = [
        ('business', 'Business Contact'),
        ('help_creator', 'Help for Creators' ),
        ('feedback', 'Feedback' ),
        ('complain', 'Complain' ),
    ]
    
    name = models.CharField(max_length= 150)
    email = models.EmailField()
    category = models.CharField(max_length= 20, choices = CATEGORY_CHOICES)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add= True)

    def __str__(self):
        return f"{self.name} - {self.get_category_display()}"