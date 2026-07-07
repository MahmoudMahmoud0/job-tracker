from django import forms
from .models import Application

class ApplicationForm(forms.ModelForm):
    quick_company_name = forms.CharField(
        required=False,
        label="Quick add company",
        help_text="Only fill this in if the company is not already in the list.",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Type a new company name",
            }
        ),
    )

    class Meta:
        model = Application
        fields = [
            "title",
            "company",
            "department",
            "source",
            "status",
            "salary_min",
            "salary_max",
            "applied_at",
            "notes",
            "tags",
            "archived"
        ]

    def __init__(self, *args, **kwargs):
        self.owner = kwargs.pop("owner", None)
        super().__init__(*args, **kwargs)

        if self.owner is not None and "tags" in self.fields:
            self.fields["tags"].queryset = self.owner.tags.all()
            self.fields["tags"].widget = forms.CheckboxSelectMultiple()
            self.fields["tags"].label = "Tags"
            self.fields["tags"].help_text = "Attach existing tags here. You can also add brand-new tags right below."

        if "company" in self.fields:
            self.fields["company"].required = False
            self.fields["company"].help_text = "Pick an existing company, or use the quick add field right below."

        if "archived" in self.fields:
            self.fields["archived"].help_text = "Use this only if you want to hide the application from the active list."


    def clean(self):
        cleaned_data = super().clean()

        company = cleaned_data.get("company")
        quick_company_name = (cleaned_data.get("quick_company_name") or "").strip()
        salary_min = cleaned_data.get("salary_min")
        salary_max = cleaned_data.get("salary_max")

        if not company and not quick_company_name:
            self.add_error(
                "company",
                "Select a company or enter a new one in Quick add company.",
            )

        if (
            salary_min is not None
            and salary_max is not None
            and salary_max < salary_min
        ):
            self.add_error(
                "salary_max",
                "Maximum salary must be greater than or equal to the minimum salary.",
            )

        return cleaned_data
