import time
import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Sum
from campaign.models import Submission, ActivatedCampaign
from earning_profile.utils import setup_browser 
from payments.models import Wallet

class Command(BaseCommand):
    help = 'Smart bot with 6-Hour Cycle, Anti-Fraud, and Total Earning Shield.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING(" Starting Master Tracking System...\n"))

        # Sirf un videos ko pakdo jo abhi tak calculate/complete nahi hui hain
        active_submissions = Submission.objects.filter(status__in=['pending', 'eligible'])

        if not active_submissions.exists():
            self.stdout.write(self.style.SUCCESS("No active videos found to update."))
            return

        driver = setup_browser()
        now = timezone.now()

        try:
            for sub in active_submissions:
                self.stdout.write(f"\nChecking Video: {sub.video_link}")

                
                # THE TOTAL EARNING SHIELD (Campaign Limit) &
                # Check karo is user ne is brand se total kitna kama liya hai
                total_earned_dict = Submission.objects.filter(
                    user=sub.user, campaign=sub.campaign
                ).aggregate(Sum('money_earned'))
                
                total_earned = total_earned_dict['money_earned__sum'] if total_earned_dict['money_earned__sum'] else Decimal('0.00')

                # Agar total limit (e.g., ₹2500) poori ho chuki hai, toh is video ko check hi mat karo! (Save RAM)
                if total_earned >= sub.campaign.max_earnings_per_creator:
                    self.stdout.write(self.style.WARNING(f"🏆 Creator has reached Max Earning Limit (₹{sub.campaign.max_earnings_per_creator}) for this campaign! Stopping checks."))
                    continue

               
                # THE 6-HOUR TIMER CHECK &
                # Pata karo aakhiri baar check kab hua tha (Agar pehli baar hai, toh submit hone ka time lo)
                last_check = sub.last_checked_at if sub.last_checked_at else sub.submitted_at
                time_diff = now - last_check
                hours_passed = time_diff.total_seconds() / 3600

                # Agar 6 ghante nahi beete hain, toh ignore karke agli video par jao
                if hours_passed < 6:
                    self.stdout.write(f"⏳ Only {hours_passed:.1f} hours passed. Waiting for 6 hours cycle.")
                    continue

           
                # FETCH DATA (Scraping)
                # Browser navigation
                driver.get(sub.video_link)
                time.sleep(random.uniform(4.0, 8.0))

                # Dummy Data (Asli HTML tags hum baad mein lagayenge)
                fetched_views = 500000 
                fetched_likes = 450     

                
                # ANTI-BOT CHECK (Engagement Ratio)
               
                if fetched_views > 0:
                    engagement_ratio = (fetched_likes / fetched_views) * 100
                    if engagement_ratio < 0.1:
                        sub.status = 'ineligible'
                        sub.save()
                        self.stdout.write(self.style.ERROR(f" Fraud: Bot views! Engagement is {engagement_ratio:.2f}%."))
                        continue

                # Agar sab theek hai toh check_count bada do aur naya time set kar do
                sub.check_count += 1
                sub.last_checked_at = now
                sub.view_count = fetched_views
                sub.eligible_views = fetched_views
                sub.status = 'eligible'

                =
                # 24-HOUR MARK: FINAL SETTLEMENT (The 4th Check)
                if sub.check_count == 4:
                    self.stdout.write("24 Hours Completed! Calculating Money...")
                    
                    calculated_money = (Decimal(sub.eligible_views) / Decimal('1000000')) * sub.campaign.rate_per_million

                    # SHIELD 1 & 2
                    if sub.campaign.max_earnings_per_post > 0 and calculated_money > sub.campaign.max_earnings_per_post:
                        calculated_money = sub.campaign.max_earnings_per_post
                    money_left_to_earn = sub.campaign.max_earnings_per_creator - total_earned
                    if calculated_money > money_left_to_earn:
                        calculated_money = money_left_to_earn

                    # Auto-Approve karega aur status 'eligible' banayega
                    sub.money_earned = calculated_money
                    sub.status = 'eligible' 
                    sub.save() 
                    
                    # Wallet mein auto-paisa daal do!
                    from payments.models import Wallet
                    wallet, created = Wallet.objects.get_or_create(user=sub.user)
                    wallet.balance_inr += calculated_money
                    wallet.save()
                    
                    self.stdout.write(self.style.SUCCESS(f"💰 Auto-Approved! Earned: ₹{calculated_money} added to Wallet!"))
                
                else:
                    self.stdout.write(self.style.SUCCESS(f" Check {sub.check_count}/4 complete. Views updated."))
                    sub.save()

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"⚠️ Error: {str(e)}"))
        finally:
            if 'driver' in locals() and driver:
                driver.quit()
                self.stdout.write("🛑 Browser closed safely.")
            self.stdout.write(self.style.SUCCESS("\n Tracking Completed!"))