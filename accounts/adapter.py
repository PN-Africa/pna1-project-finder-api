from django.conf import settings

from allauth.account.adapter import DefaultAccountAdapter


class CustomAccountAdapter(DefaultAccountAdapter):
    def get_email_confirmation_url(self, request, emailconfirmation):
        base_url = settings.FRONTEND_BASE_URL
        verify_email_path = settings.FRONTEND_VERIFY_EMAIL_PATH
        
        return (base_url + verify_email_path).format(key=emailconfirmation.key)