from django.contrib import admin
from .models import EarningAccount
from django.core.exceptions import ValidationError

@admin.register(EarningAccount)
class EarningAccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'bio_code', 'created_at')
    list_editable = ('status',) 
    
    
    def save_model(self, request, obj, form, change):
        if obj.status == 'rejected' and not obj.rejection_reason:
            raise ValidationError("Admin, write valide reason!")
        super().save_model(request, obj, form, change)