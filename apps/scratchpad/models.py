from django.db import models

class ScratchpadEntry(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    key = models.CharField(max_length=255)
    content_type = models.CharField(max_length=50)  # text, json, binary
    text_content = models.TextField(blank=True)
    json_content = models.JSONField(blank=True, null=True)
    binary_content = models.BinaryField(blank=True, null=True)
    metadata = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'key']
        verbose_name_plural = 'Scratchpad entries'
    
    def __str__(self):
        return f"{self.user.username} - {self.key}" 