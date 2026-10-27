from django.db import models
from django.conf import settings
from django.utils import timezone

class AttendanceStatus(models.TextChoices):
    PRESENT = 'present', 'Present'
    ABSENT = 'absent', 'Absent'
    LATE = 'late', 'Late'

class Attendance(models.Model):
    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField(default=timezone.now)
    check_in_time = models.TimeField(default=timezone.now)
    check_out_time = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=AttendanceStatus.choices, default=AttendanceStatus.PRESENT)
    notes = models.CharField(max_length=255, blank=True, default='')
    logged_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='logged_attendances')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-date', '-check_in_time']
        unique_together = ('member', 'date')

    def __str__(self):
        return f"{self.member.full_name} - {self.date} ({self.status})"
