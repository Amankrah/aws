from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Include your Django app URLs here
    # path('users/', include('apps.users.urls')),
    # path('scratchpad/', include('apps.scratchpad.urls')),
    # path('jobs/', include('apps.crawl_jobs.urls')),
] 