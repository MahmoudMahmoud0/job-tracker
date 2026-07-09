from django.db import models
from django.conf import settings
from companies.models import Company

class Application(models.Model):

    STATUS_CHOICES = [
        ("wishlist", "Wishlist"),
        ("applied", "Applied"),
        ("interviewing", "Interviewing"),
        ("offer", "Offer"),
        ("rejected", "Rejected"),
        ("withdrawn", "Withdrawn"),
    ]

    SOURCE_CHOICES = [
        ("linkedin", "LinkedIn"),
        ("company_site", "Company Website"),
        ("referral", "Referral"),
        ("indeed", "Indeed"),
        ("email", "Email"),
        ("other", "Other"),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="applications"
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="applications"
    )
    title = models.CharField(max_length=255)
    department = models.CharField(max_length=255, blank=True)
    source = models.CharField(
        max_length=50,
        choices=SOURCE_CHOICES,
        blank=True
    )
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default="wishlist"
    )
    salary_min = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    salary_max = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    currency = models.CharField(
        max_length=3,
        default="USD"
    )
    applied_at = models.DateField(
        null=True,
        blank=True
    )
    notes = models.TextField(blank=True)
    archived = models.BooleanField(default=False)
    tags = models.ManyToManyField(
        "Tags",
        blank=True,
        related_name="applications",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-applied_at", "-created_at"]

    def __str__(self):
        return f"{self.title} at {self.company}"

    def save(self, *args, **kwargs):
        old_status = None
        old_notes = None

        if self.pk:
            application = Application.objects.get(pk=self.pk)
            old_status = application.status
            old_notes = application.notes
        
        super().save(*args, **kwargs)

        status_changed = old_status != self.status
        notes_changed = old_notes != self.notes

        if status_changed or notes_changed:
            ApplicationStatusHistory.objects.create(
                application=self,
                status=self.status,
                notes=self.notes,
            )            

class ApplicationStatusHistory(models.Model):
    application = models.ForeignKey(
        "Application",
        on_delete=models.CASCADE,
        related_name="status_history",
    )
    status = models.CharField(
        max_length=50,
        choices=Application.STATUS_CHOICES,
    )    
    changed_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-changed_at"]

class Tags(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tags",
    )

    name = models.CharField(max_length=50)
    color = models.CharField(max_length=20, blank=True)

    class Meta:
        ordering = ["name"]
        unique_together = ["owner", "name"]

    def __str__(self):
        return self.name
    

class SavedFilter(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="saved_filters",
    )
    name = models.CharField(max_length=100)
    filters = models.JSONField(default=dict)
    sort = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ["name"]
        unique_together = ["owner", "name"]

    def __str__(self):
        return self.name
    
class FollowUp(models.Model):
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="follow_ups"
    )

    title = models.CharField(max_length=255)
    due_at = models.DateTimeField(blank=True, null=True)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["due_at", "completed", "-created_at"]

    def __str__(self):
        return self.title