from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'usage_quota', 'usage_count')
    fieldsets = UserAdmin.fieldsets + (
        ('API Keys', {'fields': ('api_key', 'firecrawl_key', 'anthropic_key')}),
        ('Usage', {'fields': ('usage_quota', 'usage_count')}),
    ) 