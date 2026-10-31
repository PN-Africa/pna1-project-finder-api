from django.contrib.auth import get_user_model
from django.conf import settings

from rest_framework import serializers
from dj_rest_auth.serializers import LoginSerializer, UserDetailsSerializer
from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import PasswordResetSerializer
from allauth.account.utils import user_pk_to_url_str

from projects.models import Simulation

def custom_url_generator(request, user, token):
    uid = user_pk_to_url_str(user)

    return settings.FRONTEND_PASSWORD_RESET_URL.format(uid=uid, token=token)


UserModel = get_user_model()


class CustomUserDetailsSerializer(UserDetailsSerializer):
    registered_at = serializers.DateTimeField(source='date_joined', read_only=True)
    is_admin = serializers.BooleanField(source='is_staff', read_only=True)

    class Meta(UserDetailsSerializer.Meta):
        fields = [
            'pk',
            'email',
            'username',
            'first_name',
            'last_name',
            'registered_at',
            'is_admin',
            'professional_role'
        ]


class CustomLoginSerializer(LoginSerializer):
    email = serializers.EmailField(required=True)
    username = None


class CustomRegisterSerializer(RegisterSerializer):
    first_name = serializers.CharField(max_length=150, required=True, allow_blank=False)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=False)
    professional_role = serializers.CharField(max_length=150, required=False, allow_blank=False)

    def validate_email(self, email):
        validated_email = super().validate_email(email)

        if UserModel.objects.filter(email=validated_email).exists():
            raise serializers.ValidationError(
                'User is already registered with this e-mail address.'
            )

        return email

    def custom_signup(self, request, user):
        try:
            user.first_name = self.validated_data.get('first_name', '')
            user.last_name = self.validated_data.get('last_name', '')
            user.professional_role = self.validated_data.get('professional_role', '')

            user.save()
        except Exception as exc:
            user.delete()
            raise exc

        return user


class UserAdminSerializer(CustomUserDetailsSerializer):
    simulations_started = serializers.SerializerMethodField()
    simulations_submitted = serializers.SerializerMethodField()

    def get_simulations_started(self, instance) -> int:
        return instance.simulations.count()

    def get_simulations_submitted(self, instance) -> int:
        return instance.simulations \
            .filter(status=Simulation.Status.SUBMITTED) \
            .count()

    class Meta(CustomUserDetailsSerializer.Meta):
        fields = [
            *CustomUserDetailsSerializer.Meta.fields,
            'simulations_started',
            'simulations_submitted',
        ]


class CustomPasswordResetSerializer(PasswordResetSerializer):
    def get_email_options(self):
        return {'url_generator': custom_url_generator}
