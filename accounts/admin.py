from django.contrib import admin
from .forms import User

admin.site.site_header = "Jon Tracker Administration"
admin.site.site_title = "Job Tracker Admin"
admin.site.index_title = "Welcome to Job Tracker"

class UserAdmin(admin.ModelAdmin):
    list_display = [
        "full_name",
        "email",
        "is_email_verified",
        "is_active",
        "is_staff",
    ]

    list_filter = ["is_email_verified", "is_staff", "is_active"]

    search_fields = ["email", "first_name", "last_name"]

    @admin.display(description="Name", ordering="first_name")
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

admin.site.register(User, UserAdmin)
