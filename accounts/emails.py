from core.email import send_html_email


def send_verification_email(user, verification_url):
    send_html_email(
        subject="Verify your Job Tracker account",
        template_name="emails/verify_email.html",
        context={
            "user": user,
            "verification_url": verification_url,
        },
        recipients=[user.email],
    )