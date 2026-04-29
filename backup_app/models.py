from django.db import models
from django.utils import timezone


class BackupRecord(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    display_name = models.CharField(max_length=255)
    file_name = models.CharField(max_length=500)
    file_ids = models.JSONField(default=list, blank=True)
    backup_date = models.DateTimeField(default=timezone.now)
    size_bytes = models.BigIntegerField(null=True, blank=True)
    parts_count = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    task_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    progress_current = models.IntegerField(default=0)
    progress_total = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ['-backup_date']

    def __str__(self):
        return f"{self.display_name} ({self.backup_date.strftime('%Y-%m-%d %H:%M')})"
