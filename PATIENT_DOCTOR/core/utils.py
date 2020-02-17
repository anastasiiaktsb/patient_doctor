

def send_mail(context, email, template, user_email):
    html_content = loader.get_template(template).render(context)
    msg = EmailMultiAlternatives(
        user_email,
        ‘message’,
        settings.DEFAULT_FROM_EMAIL,
        [email]
    )
    msg.attach_alternative(html_content, “text/html”)
    msg.send()