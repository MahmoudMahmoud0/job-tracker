from django import forms
from .models import Interview

class InterviewForm(forms.ModelForm):
    class Meta:
        model = Interview
        fields = [
            "application",
            "interview_type",
            "round_name",
            "scheduled_at",
            "duration_minutes",
            "location",
            "meeting_url",
            "notes",
            "outcome",
        ]

    def __init__(self, *args, user=None, **kwargs):
        # views should give users to kwargs, this is used to llimit the choices that appear in the form dropdown of a ModelChoiceField for the user based on his own applications (not control views as in queryset - queryset in a view just prevents the user from editing someone else's follow up)

        super().__init__(*args, **kwargs)

        self.fields["application"].queryset = user.applications.select_related("company")