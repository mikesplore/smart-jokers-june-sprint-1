from django.contrib.auth.management.commands.createsuperuser import Command as BaseCommand
from django.core.management import CommandError

class Command(BaseCommand):
    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('--user_type', type=str, help='Specify the user type for the superuser.')

    def handle(self, *args, **options):
        user_type = options.get('user_type')
        if not user_type:
            raise CommandError('You must provide a user type using --user_type.')

        super().handle(*args, **options)

        email = options.get('email')
        from users.models import User
        user = User.objects.get(email=email)
        user.user_type = user_type
        user.save()
        self.stdout.write(self.style.SUCCESS(f'Successfully created superuser with user type: {user_type}'))
