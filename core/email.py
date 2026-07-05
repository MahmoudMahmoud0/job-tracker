from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from email.mime.image import MIMEImage
from pathlib import Path

LOGO_CID = "job_tracker_logo"
LOGO_PATH = settings.BASE_DIR / "static" / "images" / "logo.png"


def _attach_default_inline_images(email):
    """
    Attach application branding used by all emails.
    """

    if not LOGO_PATH.exists():
        return

    with LOGO_PATH.open("rb") as f:
        image = MIMEImage(f.read())

    image.add_header("Content-ID", f"<{LOGO_CID}>")
    image.add_header(
        "Content-Disposition",
        "inline",
        filename=LOGO_PATH.name,
    )

    email.attach(image)

def send_html_email(
    *,
    subject,
    template_name,
    context,
    recipients,
    text_template_name=None,
):
    html_content = render_to_string(template_name, context)

    if text_template_name:
        text_content = render_to_string(text_template_name, context)
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipients,
        )
    else:
        email = EmailMultiAlternatives(
            subject=subject,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipients,
        )

    email.attach_alternative(html_content, "text/html")

    _attach_default_inline_images(email)

    email.send()