from django.db import models
from applications.models import Application

class Interview(models.Model):

    INTERVIEW_TYPE_CHOICES = [
        ("phone", "Phone"),
        ("video", "Video"),
        ("onsite", "On-site"),
        ("take_home", "Take-home Assignment"),
        ("other", "Other"),
    ]

    OUTCOME_CHOICES = [
        ("pending", "Pending"),
        ("passed", "Passed"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
        ("no_show", "No Show"),
    ]
    
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="interviews"
    )

    interview_type = models.CharField(max_length=20, choices=INTERVIEW_TYPE_CHOICES)
    round_name = models.CharField(max_length=100)
    scheduled_at = models.DateTimeField(blank=True, null=True)
    duration_minutes = models.PositiveSmallIntegerField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True)
    meeting_url = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    outcome = models.CharField(
        max_length=20,
        choices=OUTCOME_CHOICES,
        default="pending",
    )