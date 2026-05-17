from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import json
from earning_profile.models import EarningAccount
from django.http import JsonResponse
from .models import Submission, Campaign, ActivatedCampaign
from django.db.models import Sum
from fraud_guard.utils import get_trust_score_data, get_campaign_blocked_count

# Create your views here.
@login_required(login_url='login')
def campaign_list(request):
    campaigns = Campaign.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'campaign/dashboard.html', {'campaigns': campaigns})

@login_required(login_url='login')
def campaign_detail(request, pk): #pk=primary key ( campaign ID)
    campaign = get_object_or_404(Campaign, pk=pk) # fetch data or show 404

    history =Submission.objects.filter(user=request.user, campaign=campaign).order_by('-submitted_at')[:100]

    return render(request, 'campaign/detail.html',{'campaign': campaign, 'history': history})

@login_required(login_url='login')
def submit_campaign(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Login please !'})
        
    if request.method == 'POST':
        data = json.loads(request.body)
        raw_link = data.get('video_link')
        campaign_id = data.get('campaign_id')
        
        campaign = Campaign.objects.get(id=campaign_id)
        active_accounts = EarningAccount.objects.filter(user=request.user, status='active')
        if not active_accounts.exists():
            return JsonResponse({'status': 'error', 'message': 'Please verify your social account first!'})


        # 1. URL CLEANING (Tracking parameters hatao)
        video_link = raw_link.split('?')[ 0 ].lower() 
        if not video_link.endswith('/'):
            video_link += '/'

        # 2. DUPLICATE CHECK
        if Submission.objects.filter(video_link__icontains=video_link).exists():
            return JsonResponse({'status': 'error', 'message': 'This link has already been submitted!'})

        # 3. Activate & Save as 'Pending' (Bot will check ID later)
        ActivatedCampaign.objects.get_or_create(user=request.user, campaign=campaign)
        Submission.objects.create(
            user=request.user,
            campaign=campaign,
            video_link=video_link,
            status='pending'
        )
        return JsonResponse({'status': 'success'})
        
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

# Force the user to login before they can run this code
@login_required(login_url='login')
# Create the function that runs when someone clicks the 'Activate' button
def activate_campaign(request, campaign_id):

    # Step 1: Find the campaign in the database using the ID from the URL
    campaign = get_object_or_404(Campaign, id=campaign_id)

    trust_data = get_trust_score_data(request.user)
    if trust_data['is_banned']:
        messages.error(request, "Trust Score 0: You are banned from activating new campaigns! Your account is restricted.")
        return redirect('profile')

    # Step 2: Check if this user has any verified social account (status='active')
    active_social_account = EarningAccount.objects.filter(user=request.user, status='active').first()

    # Step 3: If no active social account is found, stop them right here!
    if not active_social_account:
        
        # Show a warning message to the user explaining why they were redirected
        messages.warning(request, "You must connect and verify your social account first!")
        
        # Send them directly to the 'Connect Social Account' page
        return redirect('verify_account')

    # Step 4: If they have a verified account, save the activation in the database
    # We use 'get_or_create' so if they already activated it, it won't save twice
    ActivatedCampaign.objects.get_or_create(user=request.user, campaign=campaign)

    # Show a success popup message
    messages.success(request, f"Campaign '{campaign.title}' activated successfully!")
    
    # Send them back to their profile dashboard to see the newly activated campaign
    return redirect('profile')


@login_required(login_url='login')
def campaign_tracking(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id) 
    activated_campaign = get_object_or_404(ActivatedCampaign, user=request.user, campaign=campaign)
    
    if request.method == 'POST':
        # SEQUENCE FIX: 48 Limit par naya link rokna
        blocked_count = get_campaign_blocked_count(request.user, campaign)
        if blocked_count >= 48:
            messages.error(request, "Campaign Locked! Your 48 limit has been reached for this campaign due to fake views. You cannot submit new links here.")
            return redirect('campaign_tracking', campaign_id=campaign.id)

        raw_video_link = request.POST.get('video_link')
        if raw_video_link:
            video_link = raw_video_link.split('?').lower()
            if not video_link.endswith('/'):
                video_link += '/'
            
            if Submission.objects.filter(video_link__icontains=video_link).exists():
                messages.error(request, "This link has already been submitted!")
                return redirect('campaign_tracking', campaign_id=campaign.id)
            
            Submission.objects.create(
                user=request.user,
                campaign=campaign,
                video_link=video_link,
                status='pending'
            )
            messages.success(request, "Video link submitted successfully! It is now pending bot review.")
            return redirect('campaign_tracking', campaign_id=campaign.id)

    submissions = Submission.objects.filter(user=request.user, campaign=campaign).order_by('-submitted_at')
    context = {
        'campaign': campaign,
        'submissions': submissions
    }
    return render(request, 'campaign/tracking_dashboard.html', context)