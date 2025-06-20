from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

# Create your models here.
class User(AbstractBaseUser, PermissionsMixin):
    """
    Represents a user in the system with their contact information and type.
    This model is used to store user details such as email, user type, name, phone number,
    and whether the user is currently active.
    Attributes:
        email (str): The email address of the user, must be unique.
        user_type (str): The type of user, can be one of 'member', 'visitor', 'staff', 'attachee', or 'not-sure'.
        first_name (str): The first name of the user.
        last_name (str): The last name of the user.
        phone_number (str): The phone number of the user.
        is_active (bool): Indicates if the user is currently active.
        created_at (datetime): Timestamp when the user was created.
        updated_at (datetime): Timestamp when the user was last updated.
    """
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    phone_number = models.CharField(max_length=15)
    password = models.CharField(max_length=128, default='defaultpassword')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USER_TYPE_CHOICES = (
        ('staff', 'Staff'),
        ('community', 'Community Member'),
        ('visitor', 'Visitor'),
        ('attachee', 'Attachee'),
        ('member', 'Member'),
        ('not-sure', 'Not Sure'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='community')

    # Remove any groups related field or relationship here
    # If using PermissionsMixin, we need to explicitly set:
    groups = None  # Remove the groups relationship

    objects = CustomUserManager()

    # Add the following attributes to the User model
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone_number']

    def has_module_perms(self, app_label):
        if self.is_superuser:
            return True
        return self.is_staff and self.user_type == 'staff'

    def has_perm(self, perm, obj=None):
        if self.is_superuser:
            return True
        return self.is_staff and self.user_type == 'staff'