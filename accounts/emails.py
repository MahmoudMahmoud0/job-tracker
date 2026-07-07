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


def send_email_change_request_email(user, new_email, confirmation_url):
    send_html_email(
        subject="Confirm your new Job Tracker email",
        template_name="emails/email_change_request.html",
        context={
            "user": user,
            "new_email": new_email,
            "confirmation_url": confirmation_url,
        },
        recipients=[new_email],
    )
