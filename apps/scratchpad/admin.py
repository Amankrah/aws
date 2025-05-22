from django.contrib import admin
from .models import ScratchpadEntry

@admin.register(ScratchpadEntry)
class ScratchpadEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'key', 'content_type', 'created_at', 'updated_at')
    list_filter = ('user', 'content_type', 'created_at')
    search_fields = ('user__username', 'key', 'text_content')
    readonly_fields = ('created_at', 'updated_at') 