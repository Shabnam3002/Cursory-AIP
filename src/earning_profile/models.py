from django.db import models
from django.contrib.auth.models import User
import uuid

class SocialAccount(models.Model):
    #status option
    STATUS_CHOICES =[
        ('pending', 'Pending Verification'),
        ('active', 'Verified (Active)'),
        ('rejected', 'Rejected'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField()
    social_link = models.URLField(max_length=500)

    verification_code = models.CharField(max_length=100, blank=True, null=True)


    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=' Pending ')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.status}"


class EarningAccount(models.Model):
    # Status choices jaise aapne bataya
    STATUS_CHOICES = [

        ('pending', 'Pending'),
        ('active', 'Active'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='earning_profile_accounts')
    platform_link = models.URLField() # Instagram/FB/moj/you.tb link

    #auto generated bio code
    bio_code = models.CharField(max_length=20, blank=True)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    
    created_at = models.DateTimeField(auto_now_add=True)

    rejection_reason = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.bio_code:
            #create unique code for every-single-user.
            self.bio_code = "CAIP-" + uuid.uuid4().hex[:6].upper()
        super().save(*args, **kwargs)

   