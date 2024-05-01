from rest_framework import serializers
from .models import User
from django.contrib import auth
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes
from django.utils.http import urlsafe_base64_decode
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
# import bleach


class RegisterSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(max_length=255,min_length=5)
    phone_number = serializers.CharField(required=True,max_length=20,min_length=5)
    full_name = serializers.CharField(required=True,max_length=255)
    password = serializers.CharField(max_length=68,min_length=8, write_only=True)

    class Meta:
        model = User
        fields = ['full_name','phone_number','email','password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, attrs):
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        # as long as the fields are the same, we can just use this
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

class EmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=555)

    class Meta:
        model = User
        fields = ['token']


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255,min_length=5)
    
    phone_number= serializers.CharField(
        max_length=255, min_length=7, required=False)
    full_name = serializers.CharField(
        max_length=255, min_length=3, read_only=True)
    password = serializers.CharField(
        max_length=68, min_length=6, write_only=True)


    tokens = serializers.SerializerMethodField()

    def get_tokens(self, obj):
        user = User.objects.get(email=obj['email'])

        return {
            'refresh': user.tokens()['refresh'],
            'access': user.tokens()['access']
        }

    class Meta:
        model = User
        fields = ['password', 'full_name', 'tokens','id','phone_number','email']

    def validate(self, attrs):
        email = attrs.get('email', '')
        password = attrs.get('password', '')
        filtered_user_by_email = User.objects.filter(email=email)
        user = auth.authenticate(email=email, password=password)

        # if filtered_user_by_email.exists() and filtered_user_by_email[0].auth_provider != 'phone_number':
        #     raise AuthenticationFailed(
        #         detail='Please continue your login using ' + filtered_user_by_email[0].auth_provider)

        if not user:
            raise AuthenticationFailed('Invalid credentials, try again')
        if not user.is_active:
            raise AuthenticationFailed('Account disabled, contact admin')
        if not user.is_verified:
            raise AuthenticationFailed('Account is not verified')

        # get the church for that user


        return {
            'id': user.id,
            'phone_number': user.phone_number,
            'full_name': user.full_name,
            'tokens': user.tokens,
            'is_active': user.is_active,
            'email': user.email,

        }


class GetUserProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, min_length=3)
    phone_number = serializers.CharField(
        max_length=255, min_length=3, read_only=True)
    full_name = serializers.CharField(
        max_length=255, min_length=3, read_only=True)
    id = serializers.IntegerField(read_only=True)
    profile_picture = serializers.CharField(
        max_length=255, min_length=3, read_only=True)

    class Meta:
        model = User
        fields = ['email', 'phone_number', 'full_name','id','profile_picture', 'role']

    
class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=4,required=False)
    phone_number = serializers.CharField(required=False)
    redirect_url = serializers.CharField(max_length=500, required=False)

    class Meta:
        fields = ['email','phone_number',]

class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        min_length=6, max_length=68, write_only=True)
    token = serializers.CharField(
        min_length=1, write_only=True)
    uidb64 = serializers.CharField(
        min_length=1, write_only=True)

    class Meta:
        fields = ['password', 'token', 'uidb64']

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')

            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed('The reset link is invalid', 401)

            user.set_password(password)
            user.save()

            return (user)
        except Exception as e:
            raise AuthenticationFailed('The reset link is invalid', 401)
        return super().validate(attrs)

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_message = {
        'bad_token': ('Token is expired or invalid')
    }

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):

        try:
            RefreshToken(self.token).blacklist()

        except TokenError:
            self.fail('bad_token')
            

               
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [ 'id','profile_picture']

  
class EditUserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = [ 'full_name','phone_number','email','is_active','is_staff']


class UsersSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [ 'id','full_name','phone_number','email','profile_picture','is_staff','is_active']

