from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from django.template.loader import render_to_string
from django.db import transaction
from django.contrib.sites.shortcuts import get_current_site

from rest_framework_simplejwt.token_blacklist.models import (
    OutstandingToken,
    BlacklistedToken,
)


def blacklist_user_tokens(user):
    tokens = OutstandingToken.objects.filter(user=user)

    for token in tokens:
        BlacklistedToken.objects.get_or_create(token=token)


def clear_auth_cookies(response):
    access_cookie = settings.REST_AUTH.get('JWT_AUTH_COOKIE')
    refresh_cookie = settings.REST_AUTH.get('JWT_AUTH_REFRESH_COOKIE')

    cookie_names = [access_cookie, refresh_cookie]
    for cookie_name in cookie_names:
        if cookie_name:
            response.delete_cookie(cookie_name, path='/', samesite='Lax')

    return response


def deactivate_user(user):
    with transaction.atomic():
        blacklist_user_tokens(user)

        user.is_active = False
        user.deactivated_at = timezone.now()

        user.save(update_fields=['is_active', 'deactivated_at'])


def delete_user(user):
    with transaction.atomic():
        blacklist_user_tokens(user)
        
        user.delete()


def reactivate_user(user):
    user.is_active = True
    user.deactivated_at = None

    user.save(update_fields=['is_active', 'deactivated_at'])


def send_account_email(request, *, recipient, context, template_name):
    subject_prefix = f'[{get_current_site(request).name}] '
    subject = render_to_string(f'{template_name}_subject.txt', context)

    message = render_to_string(f'{template_name}_message.txt', context)

    send_mail(
        subject=subject_prefix + subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[recipient],
        fail_silently=False
    )


def send_account_deactivation_email(request, user):
    send_account_email(
        request=request,
        recipient=user.email,
        context={'user': user},
        template_name='accounts/email/account_deactivation',
    )


def send_account_deletion_email(request, email, name):
    send_account_email(
        request=request,
        recipient=email,
        context={'name': name},
        template_name='accounts/email/account_deletion',
    )


def send_account_reactivation_email(request, user):
    send_account_email(
        request=request,
        recipient=user.email,
        context={'user': user},
        template_name='accounts/email/account_reactivation',
    )



