from django import forms
from .models import Transaction

class WithdrawalForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount_inr', 'upi_id', 'account_number', 'ifsc_code', 'account_holder_name']
        widgets = {
            'amount_inr': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Amount (Min ₹500)'}),
            'upi_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'yourname@upi'}),
            'account_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Account Number'}),
            'ifsc_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'IFSC Code'}),
            'account_holder_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        upi = cleaned_data.get("upi_id")
        acc = cleaned_data.get("account_number")
        ifsc = cleaned_data.get("ifsc_code")

        # Check both blank?
        if not upi and not (acc and ifsc):
            raise forms.ValidationError("Please provide your UPI ID or bank details, including Account Number, IFSC Code, and Account Holder Name.")
        return cleaned_data