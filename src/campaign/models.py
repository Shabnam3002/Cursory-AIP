from django.db import models
from django.contrib.auth.models import User
#from payments.models import Wallet

class Campaign(models.Model):
   
    title = models.CharField(max_length=255)
    banner_image = models.ImageField(upload_to='campaign_banners/') 
    description = models.TextField() 
    
    #money & rates
    rate_per_million = models.DecimalField(max_digits=10, decimal_places=2) 
    total_budget = models.DecimalField(max_digits=12, decimal_places=2)
    budget_used= models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    #Constraints 
    max_submissions_per_user=models.IntegerField(default=100)
    #limits of max earnings  per creator 
    max_earnings_per_creator= models.DecimalField(max_digits=10, decimal_places=2)
    #limit of max earning per post 
    max_earnings_per_post = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    supported_platforms = models.CharField(max_length=100, help_text="e.g. TikTok, Instagram", null=True, blank=True)
    #campaign requirements
    requirements=models.TextField(help_text="Detailed rules for the creators", null=True, blank=True)
    example_edits_link=models.URLField(blank=True, null=True)


    is_active = models.BooleanField(default=True)
    created_at =models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def progress_percentage(self):
        if self.total_budget > 0:
            return (self.budget_used / self.total_budget) * 100
        return 0

class ActivatedCampaign(models.Model):
    
    # Link this record to the user who is clicking the activate button
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Link this record to the specific campaign they want to work on
    campaign = models.ForeignKey('Campaign', on_delete=models.CASCADE)
    
   
    activated_at = models.DateTimeField(auto_now_add=True)

    # This function just shows a readable name in the Django adminpanel
    def __str__(self):
        # Example output: "ono098 activated JBL Campaign"
        return f"{self.user.username} activated {self.campaign.title}"

class Submission(models.Model):
   
    STATUS_CHOICES = [
        ('pending', 'Pending Bot Check'),
        ('eligible', 'Eligible (Bot Passed)'),
        ('ineligible', 'Ineligible (Time-Travel)'),
        ('fake_views', 'Fake Views Detected'),
        ('id_not_match', 'ID Not Match'),
    ]

    #ADMIN BLOCK LIMIT 48-Point System 
    ADMIN_VERIFY_CHOICES = [
        ('pending', 'Pending Admin Check'),
        ('passed', 'Passed (Money Added)'),
        ('blocked', 'Blocked (Fraud)'),
        ('unrequired', 'Unrequired (Bot Failed)'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    video_link = models.URLField()

    #tracking
    view_count = models.IntegerField(default=0)
    eligible_views = models.IntegerField(default=0)
    money_earned = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    #status Columns
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Admin Verification 'spacil'
    admin_verification = models.CharField(max_length=20, choices=ADMIN_VERIFY_CHOICES, default='pending')

    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.campaign.title}"

    def save(self, *args, **kwargs):
        # 1. Pata lagao ki ye naya submission hai ya purana (Admin edit kar raha hai)
        is_new = self.pk is None
        
        if not is_new:
            old_sub = Submission.objects.get(pk=self.pk)
            old_admin_status = old_sub.admin_verification
            old_money = old_sub.money_earned
        else:
            old_admin_status = 'pending'
            old_money = 0

        # Pehle apne data ko save hone do
        super().save(*args, **kwargs)

        from payments.models import Wallet

        if not is_new:
            # SCENARIO A: Admin ne Pending se "Passed" kar diya
            if old_admin_status != 'passed' and self.admin_verification == 'passed':
                wallet, _ = Wallet.objects.get_or_create(user=self.user)
                wallet.balance_inr += self.money_earned
                wallet.save()

            # SCENARIO B: Video already "Passed" thi, lekin Bot ne aur naye views ka paisa badha diya
            elif old_admin_status == 'passed' and self.admin_verification == 'passed':
                if self.money_earned != old_money:
                    wallet, _ = Wallet.objects.get_or_create(user=self.user)
                    difference = self.money_earned - old_money  # Naya paisa nikalo
                    wallet.balance_inr += difference
                    wallet.save()

            # SCENARIO C: Admin ne Passed video ko baad mein Fraud/Fake Views bol kar "Blocked" kar diya
            elif old_admin_status == 'passed' and self.admin_verification != 'passed':
                wallet, _ = Wallet.objects.get_or_create(user=self.user)
                wallet.balance_inr -= old_money  # Paisa wapas Wallet se kaat lo!
                wallet.save()    