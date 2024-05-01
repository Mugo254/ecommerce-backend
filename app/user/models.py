from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from rest_framework_simplejwt.tokens import RefreshToken


# Create your models here.

class CustomAccountManager(BaseUserManager):
    def create_superuser(self, full_name, email, password, **other_fields):
        

        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)
        other_fields.setdefault('is_verified', True)

        if not email:
            raise ValueError(_('You must provide an email address'))

        if not full_name:
            raise ValueError(_('You must provide the full names'))

        if other_fields.get('is_staff') is not True:
            raise ValueError(
                'Superuser must be assigned to is_staff=True.')
        if other_fields.get('is_superuser') is not True:
            raise ValueError(
                'Superuser must be assigned to is_superuser=True.')

        return self.create_user(full_name, email, password, **other_fields)

    def create_user(self, full_name, email, password, **other_fields):

        if not email:
            raise ValueError(_('You must provide an email address'))

        if not full_name:
            raise ValueError(_('You must provide the full names'))

        user = self.model(full_name=full_name,email=email,**other_fields)
        user.set_password(password)
        user.save()
        return user


AUTH_PROVIDERS = {'facebook': 'facebook', 'google': 'google',
                  'twitter': 'twitter', 'email_address': 'email_address'}



class User(AbstractBaseUser, PermissionsMixin):

    gender = (
        ('male', 'Male'),
        ('female', 'Female'), 
    )



    email = models.EmailField(_('email address'), blank=True, null=True,unique=True)
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=50, unique=True, db_index=True)
    id_number = models.CharField(max_length=255, db_index=True,null=True,blank=True)
    residence = models.CharField(max_length=255, blank=True)
    gender = models.CharField(max_length=50, choices=gender, blank=True)
    country =  models.CharField(max_length=255,null=True, blank=True)
    dob=models.DateField(blank=True,null=True)
    profile_picture = models.ImageField(upload_to='profile_pic/%Y/%m/%d/', default='default_pic.png', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    auth_provider = models.CharField(
        max_length=255, blank=False,
        null=False, default=AUTH_PROVIDERS.get('email_address'))

    is_staff = models.BooleanField(default=False)

    can_be_seen = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)

    objects = CustomAccountManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        ordering: ['-created_at']

    def __str__(self):
        return self.full_name

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }

    




    

