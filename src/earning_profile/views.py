from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages 
from .models import EarningAccount, SocialAccount
from .utils import verify_bio_code 
from fraud_guard.utils import get_trust_score_data

@login_required
def verify_account_view(request):
    account = EarningAccount.objects.filter(user=request.user).order_by('-id').first()
    if account and account.status == 'active':
        account = None

    return render(request, 'earning_profile/verify.html', {'account': account})

@login_required
def connect_account(request):
    trust_data = get_trust_score_data(request.user)
    if trust_data['is_banned']:
        messages.error(request, "Trust Score 0: You are banned from adding new social accounts! Your account is restricted.")
        return redirect('verify_account')

    if request.method == 'POST':
        social_link = request.POST.get('social_link')
        
       
        # ANTI-SCAM GUARD: DUPLICATE SOCIAL ID CHECK 
        if social_link:
            # 1. clean new link and lowecase 
            social_link_clean=social_link.strip().lower()
            # 2. Extract username from  link(e.g., 'physicsx2026') 
            submitted_username=social_link_clean.strip('/').split('/')[-1]
            
            # 3. Check all the accounts in the database
            all_accounts=EarningAccount.objects.all()
            for account in all_accounts:
                existing_username=account.platform_link.strip().lower().strip('/').split('/')[-1]
                
                # If the submitted username already exists in the database
                if submitted_username == existing_username:
                    # Show an error to the user immediately and stop the process 
                    messages.error(request, f"Scam Alert: The ID '@{submitted_username}' is already linked to another account on this platform!")
                    
                    return redirect('verify_account')

        
          # Agar koi fraud nahi mila, then create a new account then.
         #if not found any fraud, 
        EarningAccount.objects.create(

            user=request.user,
            platform_link=social_link,
            status='pending'
        )
        return redirect('verify_account')

    # if the user clicked "Try again", reset the form to show them
    account = EarningAccount.objects.filter(user=request.user).order_by('-id').first()
    if account and account.status == 'failed':
        account.delete() 
        return redirect('verify_account')
        
    return render(request, 'earning_profile/verify.html')

@login_required
def start_verification(request, account_id):
    account=get_object_or_404(EarningAccount, id=account_id, user=request.user)
    #call the scraping funtion
    success, reason=verify_bio_code(account.platform_link, account.bio_code)

    if success:
        account.status = 'active'
        account.rejection_reason = "" #remove old reason
        messages.success(request, "Now you can remove the code from bio for security. Because your account is verified.")
    else:
        account.status ='failed'
        account.rejection_reason = reason
        messages.error(request, "Attention: Our backend could not verify your profile. Please check the details below.")

    account.save()
    return redirect('verify_account')


@login_required
def delete_connected_account(request, account_id):
    # find Data  & delete it
    account = get_object_or_404(EarningAccount, id=account_id, user=request.user)
    account.delete()
    messages.success(request, "Your connected account has been removed successfully.")
    return redirect('profile') 
