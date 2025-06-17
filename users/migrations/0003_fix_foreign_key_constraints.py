from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('users', '0002_user_groups_user_is_staff_user_is_superuser_and_more'),
    ]

    operations = [
        # This empty migration will force Django to check and fix foreign key relationships
    ]
