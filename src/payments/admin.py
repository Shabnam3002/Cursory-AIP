from django.contrib import admin
from .models import Wallet, Transaction
from .models import SupportRequest

# Register your models here.

admin.site.register(Wallet)
admin.site.register(Transaction)

@admin.register(SupportRequest)
class SupportRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'category', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'email')