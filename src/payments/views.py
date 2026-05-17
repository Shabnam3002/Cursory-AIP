from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Wallet, Transaction, SupportRequest
from .forms import WithdrawalForm
from django.contrib import messages

# Create your views here.
@login_required(login_url='login')
def dashboard(request):
    # 1. Find wallet or create if not exists
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    transactions = Transaction.objects.filter(wallet=wallet).order_by('-created_at')
    
    if request.method == 'POST':
        form = WithdrawalForm(request.POST)
        if form.is_valid():
            withdrawal = form.save(commit=False)
            withdrawal.wallet = wallet
            withdrawal.status = 'PENDING'
            try:
                withdrawal.save()
                messages.success(request, "Your withdrawal request has been submitted!")
                return redirect('dashboard')
            except Exception as e:
                messages.error(request, f"Error: {e}")
    else:
        # Jab GET request aati hai (Yani page pehli baar load hota hai)
        form = WithdrawalForm()

    context = {
        'wallet': wallet,
        'transactions': transactions,
        'form': form, 
    }
    return render(request, 'payments/dashboard.html', context)

    #context = {
       # 'wallet': wallet,
       # 'transactions': transactions,
   # }
   # return render(request, 'payments/dashboard.html', context)'''

def home_page(request):
    if request.method == 'POST':
        # Form se data nikalo
        name = request.POST.get('name')
        email = request.POST.get('email')
        category = request.POST.get('category')
        description = request.POST.get('description')

        
        if name and email and category and description:
            SupportRequest.objects.create(
                name=name,
                email=email,
                category=category,
                description=description
            )
            messages.success(request, "Your message has been sent successfully! Our team will review it soon.")
            return redirect('home')

    return render(request, 'payments/home.html') 