from django.contrib import admin
from .models import CrawlJob, CrawlResult

class CrawlResultInline(admin.TabularInline):
    model = CrawlResult
    extra = 0
    readonly_fields = ('created_at',)

@admin.register(CrawlJob)
class CrawlJobAdmin(admin.ModelAdmin):
    list_display = ('user', 'query', 'status', 'created_at', 'completed_at')
    list_filter = ('status', 'created_at', 'user')
    search_fields = ('user__username', 'query', 'domain')
    readonly_fields = ('job_id', 'created_at', 'completed_at')
    inlines = [CrawlResultInline]

@admin.register(CrawlResult)
class CrawlResultAdmin(admin.ModelAdmin):
    list_display = ('crawl_job', 'title', 'url', 'content_type', 'created_at')
    list_filter = ('content_type', 'created_at')
    search_fields = ('title', 'url', 'content')
    readonly_fields = ('created_at',) 