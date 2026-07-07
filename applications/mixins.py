
from applications.models import Tags


class ApplicationTagBuilderMixin:
    AUTO_TAG_COLORS = [
        "#10b981",
        "#3b82f6",
        "#f59e0b",
        "#ef4444",
        "#8b5cf6",
        "#06b6d4",
        "#84cc16",
        "#f97316",
    ]

    def get_new_tag_rows(self):
        if self.request.method == "POST":
            names = self.request.POST.getlist("new_tag_name")
            colors = self.request.POST.getlist("new_tag_color")
            rows = []

            for index, name in enumerate(names):
                color = colors[index] if index < len(colors) else ""
                if name.strip() or color.strip():
                    rows.append({"name": name, "color": color or self.AUTO_TAG_COLORS[index % len(self.AUTO_TAG_COLORS)]})

            if rows:
                return rows

        return [{"name": "", "color": self.AUTO_TAG_COLORS[0]}]

    def should_show_new_tags(self, rows):
        return any((row.get("name") or "").strip() for row in rows)

    def get_existing_tag_picker_context(self, form):
        selected_values = form["tags"].value() or []
        selected_ids = {str(value) for value in selected_values}
        existing_tags = []

        if self.request.user.is_authenticated:
            for tag in self.request.user.tags.all():
                existing_tags.append(
                    {
                        "id": str(tag.pk),
                        "name": tag.name,
                        "color": tag.color or self.AUTO_TAG_COLORS[0],
                        "selected": str(tag.pk) in selected_ids,
                    }
                )

        return existing_tags

    def attach_new_tags(self, application):
        names = self.request.POST.getlist("new_tag_name")
        colors = self.request.POST.getlist("new_tag_color")

        for index, raw_name in enumerate(names):
            tag_name = raw_name.strip()
            if not tag_name:
                continue

            tag_color = colors[index].strip() if index < len(colors) else ""
            tag_color = tag_color or self.AUTO_TAG_COLORS[index % len(self.AUTO_TAG_COLORS)]

            tag, _ = Tags.objects.get_or_create(
                owner=self.request.user,
                name=tag_name,
                defaults={"color": tag_color},
            )
            application.tags.add(tag)

class ApplicationCompanyMixin:
    def should_show_quick_company(self, form):
        return bool(
            (form["quick_company_name"].value() or "").strip()
            or form.errors.get("quick_company_name")
            or form.errors.get("company")
        )

    def resolve_company(self, form):
        company = form.cleaned_data.get("company")
        quick_company_name = (form.cleaned_data.get("quick_company_name") or "").strip()

        if quick_company_name:
            existing_company = self.request.user.companies.filter(name__iexact=quick_company_name).first()
            if existing_company:
                return existing_company

            return self.request.user.companies.create(name=quick_company_name)

        return company
