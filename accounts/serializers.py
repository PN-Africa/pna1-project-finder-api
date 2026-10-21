from django.contrib.auth import get_user_model

from rest_framework import serializers
from dj_rest_auth.serializers import LoginSerializer, UserDetailsSerializer
from dj_rest_auth.registration.serializers import RegisterSerializer


UserModel = get_user_model()

# from accounts.models import Profile


# class ProfileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Profile
#         fields = ['professional_role']

class CustomUserDetailsSerializer(UserDetailsSerializer):
    registered_at = serializers.DateTimeField(source='date_joined', read_only=True)
    is_admin = serializers.BooleanField(source='is_staff', read_only=True)
    # profile = ProfileSerializer()

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
            # 'profile',
        ]

    # def update(self, instance, validated_data):
    #     # print("vd", validated_data)
    #     profile_data = validated_data.pop('profile', None)

    #     for attr, value in validated_data.items():
    #         setattr(instance, attr, value)

    #     instance.save()

    #     print("pd", profile_data)
    #     if profile_data is not None:
    #         profile, _ = Profile.objects.get_or_create(user=instance)

    #         print(profile)

    #         for attr, value in profile_data.items():
    #             setattr(profile, attr, value)

    #         print(profile)
    #         profile.save()

    #     return instance


class CustomLoginSerializer(LoginSerializer):
    email = serializers.EmailField(required=True)
    username = None


class CustomRegisterSerializer(RegisterSerializer):
    first_name = serializers.CharField(max_length=150, required=True, allow_blank=False)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    professional_role = serializers.CharField(max_length=150, required=False, allow_blank=True)

    def validate_email(self, email):
        validated_email = super().validate_email(email)

        if UserModel.objects.filter(email=validated_email).exists():
            raise serializers.ValidationError(
                'User is already registered with this e-mail address.'
            )

        return email

    def custom_signup(self, request, user):
        user.first_name = self.validated_data.get('first_name', None)
        user.last_name = self.validated_data.get('last_name', None)
        user.professional_role = self.validated_data.get('professional_role', None)

        user.save()

        return user