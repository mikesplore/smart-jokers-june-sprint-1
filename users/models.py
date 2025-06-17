from django.db import models

# Create your models here.
class User(models.Model):
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
    user_type = models.CharField(max_length=20, choices=[
        ('member', 'Member'),
        ('visitor', 'Visitor'),
        ('staff', 'Staff'),
        ('attachee', 'Attachee'),
        ('not-sure', 'Not Sure'),
    ])
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=15)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)