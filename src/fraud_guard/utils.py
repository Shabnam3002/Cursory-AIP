from campaign.models import Submission, ActivatedCampaign

def get_trust_score_data(user):
    """
    (Trust Score) calculate proparly .
    """
    activated_campaigns = ActivatedCampaign.objects.filter(user=user)
    locked_campaigns_list = []
    
    for ac in activated_campaigns:
        #  'blocked' links calculate every activated campaign
        blocked_count = Submission.objects.filter(
            user=user, 
            campaign=ac.campaign, 
            admin_verification='blocked'
        ).count()
        
        #if block limit greater then 48, so campaign 'Locked' 
        if blocked_count >= 48:
            locked_campaigns_list.append(ac.campaign.title)

    # 1 Locked Campaign = 1 (Heartbroken)
    broken_hearts = len(locked_campaigns_list)
    remaining_hearts = max(0, 3 - broken_hearts) # It will not be less than 3, and will not go below 0.

    # Dictionary return 
    return {
        'remaining_hearts': remaining_hearts,
        'locked_campaigns_list': locked_campaigns_list,
        'is_banned': remaining_hearts == 0  #True
    }

def get_campaign_blocked_count(user, campaign):
    """Sirf ek specific campaign ka blocked count nikalne ke liye"""
    return Submission.objects.filter(
        user=user, 
        campaign=campaign, 
        admin_verification='blocked'
    ).count()
