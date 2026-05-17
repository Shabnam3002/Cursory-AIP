#3-Hearts System
def get_trust_score_data(user):
    """
    Core Anti-Fraud Algorithm: Calculates the user's Trust Score (3-Hearts System).
    Monitors blocked/fake link submissions and manages account bans.
    """
    activated_campaigns = ActivatedCampaign.objects.filter(user=user)
    locked_campaigns_list = []

    for ac in activated_campaigns:
        # Count 'blocked' or fake links submitted by the user in this campaign
        blocked_count = Submission.objects.filter(
            user=user,
            campaign=ac.campaign,
            admin_verification='blocked'
        ).count()

        # If block limit (48) is crossed, lock the campaign and flag the user
        if blocked_count >= 48:
            locked_campaigns_list.append(ac.campaign.title)

        # 1 Locked Campaign = 1 Broken Heart
        broken_hearts = len(locked_campaigns_list)
        remaining_hearts = max(0, 3 - broken_hearts) # Minimum hearts cannot go below 0

    # Return a dictionary used across the platform for rendering UI and stopping actions
    return {
        'remaining_hearts': remaining_hearts,
        'locked_campaigns_list': locked_campaigns_list,
        'is_banned': remaining_hearts == 0  # If 0 hearts left, account is permanently banned
    }

def get_campaign_blocked_count(user, campaign):
    """Helper function to fetch specific campaign blocked count"""
    return Submission.objects.filter(
        user=user,
        campaign=campaign,
        admin_verification='blocked'
    ).count()
