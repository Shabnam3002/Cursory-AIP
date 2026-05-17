from django.contrib import admin
from .models import Campaign, ActivatedCampaign, Submission
from payments.models import Wallet 
from user_profile.models import UserProfile 
from decimal import Decimal

# Register your models here.

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display =('title', 'rate_per_million', 'total_budget', 'budget_used', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields=('title',)


@admin.register(ActivatedCampaign)
class ActivatedCampaignAdmin(admin.ModelAdmin):
    # These columns will be visible in the admin panel table
    list_display = ('user', 'campaign', 'activated_at')
    
    # Add a filter sidebar to search by campaign or date
    list_filter = ('campaign', 'activated_at')
    
    # Add a search bar to easily find a specific user
    search_fields = ('user__username', 'campaign__title')

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'campaign', 'status', 'view_count', 'money_earned')
    list_filter = ('status', 'campaign')
   
    search_fields = ('user__username', 'video_link') 
    
    # new FEATURE: isse list page se hi direct dropdown click karke status change kar sakengi!
    list_editable = ('status',) 

 #penaly + hurt logic
    def save_model(self, request, obj, form, change):
        if change: 
            old_obj = Submission.objects.get(pk=obj.pk)
            
           
            if old_obj.status == 'eligible' and obj.status == 'ineligible':
                
                # 1.  Wallet se Paisa minus karo
                wallet, _ = Wallet.objects.get_or_create(user=obj.user)
                wallet.balance_inr -= old_obj.money_earned
                if wallet.balance_inr < Decimal('0.00'):
                    wallet.balance_inr = Decimal('0.00') # Minus mein na jaye isliye 0 set karo
                wallet.save()
                
                # 2. 'money_earned' ko 0 kar do (Taaki Total Earned wale column se paisa gayab ho jaye)
                obj.money_earned = Decimal('0.00')

                # 3. User Trust Heart 
                user_profile, _ = UserProfile.objects.get_or_create(user=obj.user)
                if user_profile.trust_hearts > 0:
                    user_profile.trust_hearts -= 1
                    user_profile.save()

        super().save_model(request, obj, form, change)