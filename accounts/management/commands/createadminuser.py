from django.contrib.auth.management.commands import createsuperuser
from django.core.management import CommandError
from django.contrib.auth import get_user_model
from django.db import transaction
from django.contrib.auth.password_validation import validate_password
from getpass import getpass

class Command(createsuperuser.Command):
    help = 'Create a superuser with complete profile'

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            '--stud-no',
            dest='stud_no',
            required=False,
            help='Specify student number.',
        )
        parser.add_argument(
            '--first-name',
            dest='first_name',
            required=False,
            help='Specify first name.',
        )
        parser.add_argument(
            '--last-name',
            dest='last_name',
            required=False,
            help='Specify last name.',
        )

    def handle(self, *args, **options):
        User = get_user_model()
        database = options.get('database')

        user_data = {
            'username': options.get('username'),
            'email': options.get('email'),
            'first_name': options.get('first_name'),
            'last_name': options.get('last_name'),
        }

        # Interactive mode if fields are missing
        if not user_data['username']:
            user_data['username'] = self.get_input_data(self.username_field, "Username: ")
        if not user_data['first_name']:
            user_data['first_name'] = self.get_input_data(self.username_field, "First name: ")
        if not user_data['last_name']:
            user_data['last_name'] = self.get_input_data(self.username_field, "Last name: ")
        if not options.get('stud_no'):
            stud_no = self.get_input_data(self.username_field, "Student Number: ")
        else:
            stud_no = options.get('stud_no')

        # Handle password
        password = options.get('password')
        while password is None:
            password = getpass("Password: ")
            password2 = getpass("Password (again): ")
            if password != password2:
                self.stderr.write("Error: Your passwords didn't match.")
                password = None
                continue
            try:
                validate_password(password)
            except Exception as e:
                self.stderr.write('\n'.join(e.messages))
                password = None

        try:
            with transaction.atomic():
                user = User.objects.create_superuser(
                    username=user_data['username'],
                    email=user_data['email'],
                    password=password,
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name']
                )
                
                user.profile.stud_no = stud_no
                user.profile.user_type = '1'  # Admin
                user.profile.is_approved = True
                user.profile.save()
                
                self.stdout.write(self.style.SUCCESS(f'Superuser "{user.username}" created successfully with complete profile'))
                return None  # Return None instead of the user object

        except Exception as e:
            raise CommandError(f'Failed to create superuser: {str(e)}')
